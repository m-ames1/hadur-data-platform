# Meridian Health

## Overview

Meridian Health is a fictional Integrated Delivery Network (IDN) — a
multi-facility health system operating hospitals, outpatient clinics, and
in-house imaging services under one organizational umbrella, on a single
shared EHR platform. Meridian Health is the first data provider onboarded
into the platform.

An IDN's structure is what makes it a realistic single source for the full
breadth of clinical data below: a standalone physician's office or a single
hospital couldn't plausibly generate inpatient, outpatient, *and*
diagnostic-imaging records all at once. Meridian Health's network spans the
full population represented in this dataset — its footprint is not
artificially narrowed to a hand-picked subset of facilities.

## Data provided

Meridian Health supplies the following, spanning its full network:

**Master data**
- `patients`
- `providers`
- `organizations`

**Inpatient / acute care**
- `encounters`
- `procedures`
- `devices`
- `supplies`

**Outpatient / ambulatory care**
- `conditions`
- `allergies`
- `immunizations`
- `careplans`
- `medications`

**Diagnostic**
- `observations`
- `imaging_studies`
