# 제미나이로 중점 아이콘 만들기

`tools/gemini_prompts.py`가 만드는 문서입니다. 그림을 넣고 다시 돌리면 끝난 중점은 목록에서 빠집니다.

## 순서

1. 제미나이 새 채팅에 아래 **스타일 프롬프트**를 그대로 붙여 넣습니다.
2. 루트 파일을 열어 `묶음` 하나(중점 10개)를 붙여 넣습니다. 그림이 덜 나오면 "계속"이라고 보냅니다.
3. 그림을 적힌 파일 이름(예: `LR_NAP_eagles.png`)으로 `docs/art/goals/`에 저장합니다.
4. `python tools/build_all.py --only custom_icons check_mod`를 돌립니다. 초록 배경은 자동으로 지워지고 크기도 맞춰집니다.

스타일이 흐트러지면 마음에 드는 그림 하나를 첨부하고 "이 그림과 같은 화풍으로"라고 덧붙이면 됩니다.
채팅이 길어지면 새 채팅을 열고 스타일 프롬프트부터 다시 보냅니다.

## 스타일 프롬프트

```text
You are drawing national focus icons for a Hearts of Iron IV mod, "The Belated Revolution".
Setting: an alternate 1936. France lost the Great War in 1918; Britain, the German states and Austria-Hungary won.
A beaten, half-ruined France now chooses between a restored king, a new Napoleon, a republic or a commune.

Draw every icon in the style of the vanilla Hearts of Iron IV focus icons:
- one clear object or emblem, centred, filling about 80% of the square, slightly seen from three-quarters above;
- painted, semi-realistic, with crisp dark outlines, soft lighting from the top left and a small drop shadow;
- muted, slightly desaturated period colours (brass, steel, olive, navy, parchment, dark red); 1930s look;
- readable at 95 x 95 pixels: big simple shapes, no fine detail, no tiny figures;
- NO text, letters, numbers or captions; NO border, frame, circle badge or vignette;
- background: a single flat pure green (#00FF00) with nothing else on it, so it can be cut out.
  Do not use that green inside the icon itself.
- square image, 1:1.

French symbols to use where they fit: the tricolour; the white Bourbon flag with golden fleurs-de-lis (kings);
the imperial eagle and the bee (Napoleon); the Phrygian cap and Marianne (republic); the red flag (commune);
the black-and-red flag (anarchists); the francisque axe (Pétain's État français).

I will send you focuses as "file name / route / focus name / what the focus does". Draw one image per focus,
in order, and tell me the file name above each image so I can save it under that name.
```

## 루트별 목록 — 남은 중점 20개

| 루트 | 남은 중점 |
|---|---|
| [공통](FRA.md) | 18 |
| [코뮌](COM.md) | 2 |
