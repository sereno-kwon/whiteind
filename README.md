# White Industries Korea

white.rubiworkshop.com 원페이지 정적 사이트. paul.rubiworkshop.com · thm.rubiworkshop.com과 같은 구조와 디자인(레이아웃, 서체, 빌드 방식)입니다.

- `index.html` 한국어 원페이지 (White · Range · Hubs · Cranks · Drivetrain · Headsets · Fit · Story · Showroom)
- 디자인은 rubi.kr 체계: 영문 Pretendard · 한글 에스코어 드림, 웨이트 400, 흑백과 얇은 라인, 각진 버튼, 라이트/다크 자동. 일본어 페이지는 빌드 시 Noto Sans JP로 바뀝니다.
- Paul 사이트와 같은 보정: 제품 사진은 1:1 흰 바탕에 잘리지 않게(contain), 라이프스타일 사진은 3:2, 히어로의 제품 슬라이드는 `light` 클래스로 흰 무대. 포인트 컬러는 블루(#2f5da6)로 포커스 표시에만 씁니다.
- 자바스크립트가 꺼져 있어도 본문이 보이도록 등장 모션은 `html.js`일 때만 적용합니다.
- `index.src.html` 편집용 한국어 원본. 호환 표는 `{{HUB_TABLE}}`, `{{CRANK_TABLE}}` 자리에 빌드 시 채워집니다 (`tools/build.py` 안의 HUBS, CRANKS).
- `en/index.html`, `ja/index.html` 영어 · 일본어 페이지 (빌드로 생성, 직접 수정하지 않음)
- `i18n/tr_source.py` 한국어 · 영어 · 일본어 번역 묶음, `en.json` · `ja.json`은 여기서 생성
- `404.html` 하위 주소(/cld, /r30, /eno, /vbc, /headset, /fit, /dealers 등)를 섹션으로 연결
- `.github/image-manifest.txt` + `fetch-images.yml` 화이트 인더스트리 공식 사이트(whiteind.com) 이미지 이전용 워크플로

## 처음 올릴 때
1. 저장소 `sereno-kwon/whiteind`에 이 폴더를 main에 푸시합니다.
2. 푸시하면 `fetch-images.yml`이 매니페스트의 이미지 36개를 whiteind.com에서 받아 `images/`에 커밋합니다.
3. 배포: Cloudflare Pages(저장소 연결, 빌드 명령 없음, 출력 폴더 `/`) 또는 GitHub Pages.
4. 도메인 DNS에 `white` CNAME 레코드를 추가합니다. CNAME 파일은 이미 들어 있습니다.
5. 파비콘은 별도로 넣어야 합니다: `images/favicon-48.png`, `images/favicon-96.png`, `images/apple-touch-icon.png`(180px), `images/logo-512.png`.
6. 로고(`images/logo.png`)는 whiteind.com 헤더 로고를 받아 옵니다. CSS에서 헤더는 검정, 다크모드는 흰색으로 칠해집니다. 받은 로고가 워드마크가 아니면 크기를 조정해야 합니다.

## 이미지
- 제품 컷과 아카이브 사진(`images/history/`)은 whiteind.com 공식 이미지입니다. 라다비스트 · 바이크패킹 사진은 저작권 때문에 쓰지 않고 Story 섹션에 링크로만 소개합니다.
- 아카이브 사진은 1024px이라 크게 쓰지 않았습니다. 루비에서 직접 찍은 사진이 있으면 `images/brand/`, `images/history/`에 덮어쓰는 것을 권합니다.

## 문구 수정과 번역
1. `index.src.html`의 한국어 문구를 고칩니다.
2. `python3 tools/build.py` → `python3 i18n/extract.py` 로 `ko.json`을 갱신합니다.
3. 바뀐 문장을 `i18n/tr_source.py`에서 같은 한국어 키로 고치거나 (한국어, 영어, 일본어)로 추가하고 `python3 i18n/tr_source.py`.
4. 다시 `python3 tools/build.py`. 번역되지 않은 문장이 있으면 목록으로 알려줍니다.

빌드에는 `beautifulsoup4`가 필요합니다.

## 링크
- 헤더 Shop, "루비워크샵에서 보기" 버튼: `https://rubiworkshop.com/white`
- 거래처 문의: 루비서플라이 02-516-8465, 카카오톡 채널 `https://pf.kakao.com/_NFnBj/chat`
- 푸터 Instagram: `https://www.instagram.com/rubi.workshop`

## 한글 표기
화이트 인더스트리(White Industries), 더그 화이트(Doug White), 알렉 화이트(Alec White), 페탈루마(Petaluma), 인버네스(Inverness), 페거스(Peggers), 크레이그 미첼(Craig Mitchell), 찰리 켈리(Charlie Kelly), 롤프 프리마(Rolf Prima), 아스트랄 사이클링(Astral Cycling), 엔듀로(Enduro), 브롬톤(Brompton). 제품명 CLD, XMR, T11, MI5, MET, ENO, VBC, R30, G30, M30, A30은 원문 표기.

## 출처
- 수치: whiteind.com 제품별 Specs, 허브 가이드, MR30 크랭크 비교표 (2026-11 확인)
- 브랜드 스토리: The Radavist 「Inside / Out at White Industries in Petaluma, California」(2018), whiteind.com 「Where We Started」, Bikepacking.com 「Inside White Industries: Five Decades of Outlasting Trends」(2026)
