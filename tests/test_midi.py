from dataclasses import replace
from io import BytesIO
import unittest
import mido
from packages.music.midi import read_midi, write_midi

def serialize(tracks, kind=1, resolution=480):
    midi = mido.MidiFile(type=kind, ticks_per_beat=resolution)
    midi.tracks.extend(mido.MidiTrack(track) for track in tracks)
    stream = BytesIO()
    midi.save(file=stream)
    return stream.getvalue()

def on(note=60, time=0, channel=0, velocity=80):
    return mido.Message('note_on', note=note, time=time, channel=channel, velocity=velocity)

def off(note=60, time=480, channel=0):
    return mido.Message('note_off', note=note, time=time, channel=channel, velocity=30)

class MidiTests(unittest.TestCase):
    def test_default_tempo_and_zero_velocity_off(self):
        score = read_midi(serialize([[on(), on(60, time=480, velocity=0)]], kind=0))
        note = score.to_dict()['notes'][0]
        self.assertEqual(note['duration_quarters'], 1)
        self.assertAlmostEqual(note['duration_seconds'], .5)
        self.assertIsNone(note['role'])
        self.assertEqual(score.notes[0].release_velocity, 0)

    def test_tempo_change_inside_note_and_multiple_tracks(self):
        score = read_midi(serialize([
            [mido.MetaMessage('set_tempo', tempo=500000), mido.MetaMessage('set_tempo', tempo=1000000, time=480)],
            [on(), off(time=960)],
            [on(48, time=480, channel=1), off(48, time=480, channel=1)]
        ]))
        rows = score.to_dict()['notes']
        self.assertAlmostEqual(rows[0]['duration_seconds'], 1.5)
        self.assertAlmostEqual(rows[1]['start_seconds'], .5)
        self.assertAlmostEqual(rows[1]['duration_seconds'], 1)
        self.assertEqual(rows[1]['channel'], 1)

    def test_chords_repetition_and_channels(self):
        score = read_midi(serialize([[on(60), on(64), on(60, channel=1),
           off(60), off(64, time=0), off(60, time=0, channel=1), on(60), off(60)]]))
        self.assertEqual(len(score.notes), 4)
        self.assertEqual(read_midi(write_midi(score)).to_dict(), score.to_dict())

    def test_roundtrip_preserves_controllers_program_meter_trailing_silence(self):
        score = read_midi(serialize([[
            mido.MetaMessage('track_name', name='Piano'),
            mido.MetaMessage('time_signature', numerator=3, denominator=4),
            mido.Message('program_change', program=0),
            mido.Message('control_change', control=64, value=127), on(), off(),
            mido.Message('control_change', control=64, value=0, time=480),
            mido.MetaMessage('end_of_track', time=480)
        ]]))
        rebuilt = read_midi(write_midi(score))
        self.assertEqual(rebuilt.to_dict(), score.to_dict())
        self.assertAlmostEqual(rebuilt.to_dict()['duration_seconds'], 1.5)
        self.assertAlmostEqual(rebuilt.to_dict()['notes'][0]['duration_seconds'], .5)

    def test_symbolic_edit_changes_export(self):
        score = read_midi(serialize([[on(), off()]], kind=0))
        score.notes[0] = replace(score.notes[0], pitch=67, velocity=50, end_tick=960)
        result = read_midi(write_midi(score))
        self.assertEqual(result.notes[0].pitch, 67)
        self.assertEqual(result.notes[0].velocity, 50)
        self.assertAlmostEqual(result.to_dict()['notes'][0]['duration_seconds'], 1)

    def test_invalid_and_unsupported_inputs(self):
        cases = [b'not midi', serialize([[on(), off()]], kind=2),
                 serialize([[on(), off()]], resolution=-24), serialize([[on()]]),
                 serialize([[off()]]), serialize([[on(), on(), off(), off()]])]
        for data in cases:
            with self.subTest(data=data[:20]), self.assertRaises(ValueError):
                read_midi(data)

    def test_zero_length_note_and_empty_track(self):
        score = read_midi(serialize([[], [on(), off(time=0)]]))
        self.assertEqual(read_midi(write_midi(score)).to_dict(), score.to_dict())

    def test_sysex_warning_and_pitch_bend_preserved(self):
        score = read_midi(serialize([[mido.Message('sysex', data=[1,2]),
            mido.Message('pitchwheel', pitch=10), on(), off()]]))
        self.assertEqual(len(score.warnings), 2)
        rebuilt = read_midi(write_midi(score))
        self.assertTrue(any(e.message['type'] == 'pitchwheel' for e in rebuilt.events))
        self.assertFalse(any(e.message['type'] == 'sysex' for e in rebuilt.events))

    def test_cli_writes_json_and_midi_without_overwriting(self):
        import json
        import subprocess
        import sys
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, target, output = root / 'in.mid', root / 'out.mid', root / 'notes.json'
            source.write_bytes(serialize([[on(), off()]], kind=0))
            command = [sys.executable, 'scripts/inspect_midi.py', str(source), '--json', str(output), '--midi', str(target)]
            first = subprocess.run(command, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(output.read_text())['notes'][0]['pitch'], 60)
            self.assertEqual(read_midi(target.read_bytes()).notes[0].end_tick, 480)
            before = output.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), before)
