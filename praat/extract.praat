# Extract pitch and intensity from an audio file.
# Usage: praat --run extract.praat <audio file> <time step> <pitch floor> <pitch ceiling>
# Prints a tab-separated table (Time_s, F0_Hz, Intensity_dB) to stdout.
# Undefined values are printed as "nan". Time step 0 means Praat's automatic value.

form Extract
    sentence Audio_file
    real Time_step 0
    positive Pitch_floor 75
    positive Pitch_ceiling 600
endform

sound = Read from file: audio_file$
n_channels = Get number of channels
if n_channels > 1
    sound = Convert to mono
endif

selectObject: sound
pitch = To Pitch: time_step, pitch_floor, pitch_ceiling
selectObject: sound
intensity = To Intensity: pitch_floor, time_step, "yes"

# sample intensity on pitch frames so both share one time axis
selectObject: pitch
n = Get number of frames
writeInfoLine: "Time_s", tab$, "F0_Hz", tab$, "Intensity_dB"
for i to n
    selectObject: pitch
    t = Get time from frame number: i
    f0 = Get value in frame: i, "Hertz"
    selectObject: intensity
    db = Get value at time: t, "cubic"

    if f0 = undefined
        f0$ = "nan"
    else
        f0$ = fixed$(f0, 6)
    endif
    if db = undefined
        db$ = "nan"
    else
        db$ = fixed$(db, 6)
    endif
    appendInfoLine: fixed$(t, 6), tab$, f0$, tab$, db$
endfor
