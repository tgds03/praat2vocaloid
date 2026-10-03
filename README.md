# praat2vocaloid

음원 파일을 Praat로 분석해 그 정보를 Vocaloid vpr 파일에 삽입하는 것을 목표로 함.
현재 note start/end와 pitch(PB, PBS), intensity(DYN)을 vpr에 삽입하고 있음. 아직 CLI만 지원.

## 요구사항

- Python 3
- [Praat](https://www.fon.hum.uva.nl/praat/) 6.x (macOS: `brew install --cask praat`)
  - `--praat` 옵션, `PRAAT_PATH` 환경변수, `PATH`, 기본 설치 경로 순으로 실행 파일을 찾음

## 사용법

```
python main.py input.vpr voice.wav [--out OUT] [--start-offset MS] [--tone-offset N] [--dyn-range MIN MAX]
                                   [--praat PATH] [--pitch-floor 75] [--pitch-ceiling 600] [--time-step 0]
```

분석은 [praat/extract.praat](praat/extract.praat)를 `praat --run`으로 실행해 수행함.

## TODO

- [X] note별로 PB 및 PBS 따로 계산
- [ ] pitch 불명확한 구간을 보간으로 처리
- [ ] GUI 환경 추가
- [X] part 길이 조정
- [ ] voicebank 선택
- [ ] 음소 인식?

