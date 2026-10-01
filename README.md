# praat2vocaloid

praat 등의 음원 분석 프로그램으로 추출한 csv파일의 정보를 Vocaloid vpr 파일에 삽입하는 것을 목표로 함.
현재 note start/end와 pitch(PB, PBS), intensity(DYN)을 vpr에 삽입하고 있음. 아직 CLI만 지원.

## TODO

- note별로 PB 및 PBS 따로 계산
- pitch 불명확한 구간을 보간으로 처리
- 실행 옵션 추가
- GUI 환경 추가
- part 길이 조정
- voicebank 선택
- 음소 인식?