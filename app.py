from __future__ import annotations

from pathlib import Path

import streamlit as st

from free_video_generator import (
    LANG_DISPLAY_NAMES,
    LANG_OPTIONS,
    VideoConfig,
    create_study_video,
    get_free_script,
    parse_manual_items,
)


st.set_page_config(
    page_title="무료 다국어 학습 숏츠 생성기",
    page_icon="🎬",
    layout="centered",
)

FIXED_ILLUSTRATION_STYLE = "clean"

st.title("🎬 무료 다국어 학습 숏츠 생성기")
st.caption("OpenAI API 없이, 무료 내장 표현/직접 입력 + 무료 gTTS 음성 + 깔끔한 교육용 일러스트 배경 + 고정 인트로로 mp4를 만듭니다.")

with st.expander("이번 버전 특징", expanded=True):
    st.markdown(
        """
        - OpenAI API를 사용하지 않습니다.
        - API Key 입력칸도 없습니다.
        - 대본은 내장 표현 데이터 또는 직접 입력으로 만듭니다.
        - 음성은 무료 `gTTS`를 사용합니다.
        - 배경은 **깔끔한 교육용 그림체**로 고정되어 있습니다.
        - 주제에 따라 공항/카페/여행/DM/학교/음식 등 오브젝트만 바뀌고,
          전체 그림체와 분위기는 항상 동일하게 유지됩니다.

        즉, 계정 톤을 맞추기 위해 **그림체 하나로 고정**했고, 추가로 **1초 인트로 카드 / 고정 제목 박스 / 같은 자막 등장감**까지 넣은 버전입니다.
        """
    )

with st.sidebar:
    st.header("영상 설정")

    selected_lang_name = st.selectbox("학습 언어", list(LANG_OPTIONS.keys()), index=0)
    target_lang = LANG_OPTIONS[selected_lang_name]

    is_shorts = st.radio("영상 비율", ["쇼츠 9:16", "롱폼 16:9"], index=0) == "쇼츠 9:16"

    words = st.slider("표현 개수", min_value=3, max_value=8, value=5, step=1)

    shadowing_pause = st.slider("따라 말하기 간격", 1.0, 5.0, 2.2, 0.5)

    st.divider()
    st.header("음성 설정")

    use_tts = st.checkbox("무료 TTS 사용", value=True)
    slow_tts = st.checkbox("천천히 말하기", value=False)

    st.divider()
    st.header("배경 설정")

    use_illustration_bg = st.checkbox(
        "고정 일러스트 배경 사용",
        value=True,
        help="깔끔한 교육용 스타일로 고정된 배경입니다.",
    )

    st.info("현재 그림체: 깔끔한 교육용 (고정)")
    st.info("고정 요소: 1초 인트로 / 고정 제목 박스 / 같은 자막 등장감")
    st.info("assets/bg_loop.mp4가 있으면 그 영상이 배경으로 우선 적용됩니다.")

    use_bgm = st.checkbox("BGM 사용", value=Path("assets/bgm.mp3").exists())
    bgm_volume = st.slider("BGM 볼륨", 0.0, 0.25, 0.07, 0.01)

    use_bg_video = st.checkbox(
        "내 배경 영상 사용",
        value=Path("assets/bg_loop.mp4").exists(),
        help="assets/bg_loop.mp4가 있으면 일러스트 배경보다 우선 적용됩니다.",
    )

st.subheader("콘텐츠 입력")

topic = st.text_input(
    "영상 주제",
    placeholder="예: 공항, 카페, 여행, 학교, 음식점, DM, 기본 회화",
)

source_mode = st.radio(
    "대본 방식",
    ["무료 내장 표현 자동 선택", "직접 입력"],
    horizontal=True,
)

items = []

if source_mode == "무료 내장 표현 자동 선택":
    if topic:
        items = get_free_script(topic, target_lang, words)
        st.markdown("#### 생성될 표현 미리보기")
        st.table(items)
    else:
        st.info("주제를 입력하면 내장 표현에서 어울리는 표현을 골라 보여줍니다.")

else:
    st.markdown(
        """
        아래 형식으로 입력하세요.

        ```txt
        한국어 뜻 | 외국어 표현 | 짧은 설명
        안녕하세요 | Hola | 기본 인사
        감사합니다 | Gracias | 고마울 때 사용
        ```
        """
    )

    default_target = {
        "es": "Hola",
        "en": "Hello",
        "ja": "こんにちは",
        "zh": "你好",
        "fr": "Bonjour",
        "de": "Hallo",
        "it": "Ciao",
    }.get(target_lang, "Hello")

    default_thanks = {
        "es": "Gracias",
        "en": "Thank you",
        "ja": "ありがとうございます",
        "zh": "谢谢",
        "fr": "Merci",
        "de": "Danke",
        "it": "Grazie",
    }.get(target_lang, "Thank you")

    default_manual = f"""안녕하세요 | {default_target} | 기본 인사
감사합니다 | {default_thanks} | 고마울 때 사용
실례합니다 | Excuse me | 말을 걸 때 사용"""
    manual_text = st.text_area("직접 입력", value=default_manual, height=180)
    items = parse_manual_items(manual_text, target_lang)

    if items:
        st.markdown("#### 입력된 표현 미리보기")
        st.table(items)

st.markdown("#### 배경 방식")
if use_bg_video and Path("assets/bg_loop.mp4").exists():
    st.info("assets/bg_loop.mp4를 배경 영상으로 사용합니다.")
elif use_illustration_bg:
    st.info("깔끔한 교육용 고정 그림체 배경을 사용합니다.")
else:
    st.info("단색 배경으로 제작합니다.")

generate = st.button("🔥 무료로 영상 생성하기", use_container_width=True)

if generate:
    if not topic.strip() and source_mode == "무료 내장 표현 자동 선택":
        st.error("주제를 입력하세요.")
        st.stop()

    if not items:
        st.error("생성할 표현이 없습니다.")
        st.stop()

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    cfg = VideoConfig(
        is_shorts=is_shorts,
        shadowing_pause=float(shadowing_pause),
        words_per_topic=int(words),
        output_dir=output_dir,
        target_lang=target_lang,
        use_tts=use_tts,
        slow_tts=slow_tts,
        use_illustration_bg=use_illustration_bg,
        illustration_style=FIXED_ILLUSTRATION_STYLE,
        bgm_path="assets/bgm.mp3" if use_bgm else None,
        bgm_volume=float(bgm_volume),
        bg_video_path="assets/bg_loop.mp4" if use_bg_video else None,
    )

    progress_box = st.empty()

    def ui_progress(message: str):
        progress_box.info(message)

    with st.status("영상 생성 중", expanded=True) as status:
        try:
            output_path = create_study_video(
                topic=topic.strip() or "manual",
                items=items[:words],
                cfg=cfg,
                progress_callback=ui_progress,
            )
            status.update(label="영상 생성 완료", state="complete", expanded=False)

            st.success("완성됐습니다.")
            st.subheader("미리보기")
            st.video(str(output_path))

            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 mp4 다운로드",
                    data=f,
                    file_name=output_path.name,
                    mime="video/mp4",
                    use_container_width=True,
                )

        except Exception as e:
            status.update(label="영상 생성 실패", state="error", expanded=True)
            st.exception(e)
            st.error("오류가 났습니다. 그래도 유료 API 비용은 발생하지 않습니다.")
