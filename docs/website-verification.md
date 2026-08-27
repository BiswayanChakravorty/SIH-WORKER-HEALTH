# Static Website Verification

The standalone browser page was opened from the static `docs/` directory and verified to render the Worker Health Band header, six sensor readings, worker-tracking location card, source-linked Reading / Standard / Status table, and gas-alarm control.

The **Run gas alarm test** interaction was verified. It changes the page to an unsafe-gas state, updates oxygen to 18.7% O₂, methane to 1.7% CH₄, and carbon monoxide to 61 ppm, replaces the test control with acknowledgement and reset actions, and retains the instruction that acknowledgement does not resolve the hazard.
