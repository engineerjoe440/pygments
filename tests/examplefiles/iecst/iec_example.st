(* simple state machine *)
TxtState := STATES[StateMachine];

CASE StateMachine OF
   1: ClosingValve();
      StateMachine := 2;
   2: OpeningValve();
ELSE
    BadCase();
END_CASE;