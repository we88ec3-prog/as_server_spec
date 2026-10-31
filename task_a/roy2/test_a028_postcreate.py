"""A028 strict synthetic Native NewUser S02 and UI follow-up tests."""
import unittest
from a028_postcreate_model import NativeCreationError, s02_decoded_body, synthetic_response


class NewUserTerminalTests(unittest.TestCase):
    def test_s02_status0_empty(self):
        self.assertEqual(s02_decoded_body(b"\0\0"),(0,b""))
    def test_s02_error_with_encoded_raw_bytes(self):
        self.assertEqual(s02_decoded_body(b"\x11\x02\xa4\xa4"),(17,b"\xa4\xa4"))
    def test_s02_reject_short(self):
        for b in (b"",b"\0"):
            with self.subTest(b=b),self.assertRaises(NativeCreationError):
                s02_decoded_body(b)
    def test_s02_reject_trailing(self):
        with self.assertRaises(NativeCreationError):
            s02_decoded_body(b"\x01\0x")
    def test_s02_reject_truncated_len(self):
        with self.assertRaises(NativeCreationError):
            s02_decoded_body(b"\x01\x02x")
    def test_s02_max255_bytes(self):
        body=b"\x01\xff"+b"a"*255
        self.assertEqual(len(s02_decoded_body(body)[1]),255)
    def test_s02_reject_nonbytes(self):
        for value in ("hello",None,3):
            with self.subTest(value=value),self.assertRaises(NativeCreationError):
                s02_decoded_body(value)
    def test_state1d_success_emits_native_c04(self):
        r=synthetic_response(0x1D,0,0,appearance=(0,1,2,3,4))
        self.assertEqual(r.outgoing,((4,b"\x00\x01\x02\x03\x04"),))
        self.assertEqual(r.state_after,0x1E)
    def test_state1d_success_does_not_transfer(self):
        r=synthetic_response(0x1D,0,3,appearance=(255,0,1,2,3))
        self.assertFalse(r.auto_c03_proven)
        self.assertFalse(r.world_transfer_proven)
        self.assertFalse(r.login_pane_constructed)
    def test_state1d_requires_five_appearance_bytes(self):
        for a in (None,(1,),(1,2,3,4,5,6),(1,2,3,4,-1),(1,2,3,4,256),(1,2,3,4,True)):
            with self.subTest(a=a),self.assertRaises(NativeCreationError):
                synthetic_response(0x1D,0,3,appearance=a)
    def test_state1e_success_cleans_ui_four_slots(self):
        r=synthetic_response(0x1E,0,0)
        self.assertEqual(r.clear_ui_slots,(12,11,13,7))
        self.assertEqual(r.outgoing,())
        self.assertEqual(r.state_after,0x1E)
    def test_region3_constructs_login_pane_without_proven_c03(self):
        r=synthetic_response(0x1E,0,3)
        self.assertTrue(r.login_pane_constructed)
        self.assertFalse(r.auto_c03_proven)
        self.assertFalse(r.world_transfer_proven)
    def test_other_regions_no_region3_login_pane_ctor(self):
        for region in (0,1,2,4,5):
            with self.subTest(region=region):
                self.assertFalse(synthetic_response(0x1E,0,region).login_pane_constructed)
    def test_other_state_success_not_evidence_of_character_commit(self):
        r=synthetic_response(0x1F,0,3)
        self.assertEqual(r.state_after,0x1F)
        self.assertEqual(r.outgoing,())
        self.assertFalse(r.world_transfer_proven)
    def test_nonzero_c15_empty_and_state1f(self):
        for state in (0x1D,0x1E):
            for status in (1,2,3,17,31,255):
                with self.subTest(state=state,status=status):
                    r=synthetic_response(state,status,0,encoded_message=b"not-real-server-error")
                    self.assertEqual(r.outgoing,((0x15,b""),))
                    self.assertEqual(r.state_after,0x1F)
    def test_special_first_focus_only(self):
        for status in (3,4,18,26,31):
            self.assertEqual(synthetic_response(0x1E,status,0).focus,"first")
    def test_special_second_focus_only(self):
        self.assertEqual(synthetic_response(0x1D,17,0).focus,"second")
    def test_other_status_focus_unknown(self):
        for status in (0,1,2,5,16,19,32,255):
            self.assertIsNone(synthetic_response(0x1E,status,0).focus)
    def test_region3_state1e_suppresses_text_modal_only(self):
        self.assertFalse(synthetic_response(0x1E,1,3,encoded_message=b"no modal").message_modal_candidate)
        self.assertTrue(synthetic_response(0x1D,1,3,encoded_message=b"modal").message_modal_candidate)
        self.assertTrue(synthetic_response(0x1E,1,2,encoded_message=b"modal").message_modal_candidate)
    def test_empty_message_never_creates_message_modal(self):
        self.assertFalse(synthetic_response(0x1D,1,0).message_modal_candidate)
    def test_reject_bad_status_state_region(self):
        for args in ((-1,0,0),(0x1D,-1,0),(0x1D,0,256),(0x1D,True,1),(0x1D,0,"3")):
            with self.subTest(args=args),self.assertRaises(NativeCreationError):
                synthetic_response(*args)
    def test_reject_nonbytes_message_and_excess(self):
        for message in ("text",None,b"x"*256):
            with self.subTest(message=type(message)),self.assertRaises(NativeCreationError):
                synthetic_response(0x1E,1,0,encoded_message=message)


if __name__=="__main__":
    unittest.main()
