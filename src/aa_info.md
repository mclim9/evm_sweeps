# EVM Sweeps documentation

## Idea
- {standard}_{instr}_meas.py
  - Each standard/Instrument combo combined into a file.
  - {standard}_{instr}_meas.py will have same function names.
  - Run std_config and std_meas to verify.

## Questions
- Tests: STN; EVM; ACLR
- Is measurement within current range?
- Is test time within current range?
- Are these the right steps?

## Instrument Plan
- Start w/ FSW/SMW
- See if FSVA/SMM would work
- Eventually EVO

## Implementation plan
- Phase1: R&S Scripts
  - Validate test time & value: STN; EVM; ACLR
  - Verify steps taken
  - Add customer "complexity"
  - Identify instrument; test; & cost
- Phase2: R&S Script in Customer lab
  - "Semi Automatic test"
  - R&S Script controls R&S equipment only.
  - Customer SW controls everything else
    - DUT
    - Switch matrix
    - Pwr Supply; Pwr Meter; Scope; LoadPull etc
- Phase3: Customer integration
  - R&S AE helps customer integrate code into their framework
  - Customer writes R&S Driver
  - Customer verifies test in customer code
