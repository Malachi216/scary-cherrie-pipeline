import os, json, time
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from core.thumbnail_brief import build_thumbnail_brief
from core.research_gemini import gemini_find_cases
from core.fact_spine import build_fact_spine
from core.write_claude import claude_write_full_script
from core.split_acts import split_into_acts
from core.validate_rubric import score_act_bundle
from core.patch_rewrite import patch_rewrite_weak_blocks
from core.export_docx import export_script_docx
from core.utils import word_count, ensure_run_dir, save_json

load_dotenv()

st.set_page_config(page_title="Scary Cherrie Pipeline", layout="wide")
st.title("Thumbnail → Real Case Spine → Strict Script → Act Validation → DOCX")

# Sidebar controls
st.sidebar.header("Controls")
tone_preset = st.sidebar.selectbox(
    "Tone preset",
    ["Strict", "Aggressive", "Hard Cliffhanger", "Smooth Act1 Handoff"],
    index=0
)
min_words = st.sidebar.number_input("Min words", value=7000, step=100)
max_words = st.sidebar.number_input("Max words", value=10000, step=100)
max_fix_passes = st.sidebar.number_input("Max fix passes", value=2, step=1)

st.sidebar.divider()
st.sidebar.caption("Keys must exist in environment.")
has_gemini = bool(os.getenv("GEMINI_API_KEY"))
has_claude = bool(os.getenv("ANTHROPIC_API_KEY"))
st.sidebar.write(f"Gemini key: {'✅' if has_gemini else '❌'}")
st.sidebar.write(f"Claude key: {'✅' if has_claude else '❌'}")

tabs = st.tabs(["1) Inputs", "2) Thumbnail Brief", "3) Research", "4) Fact Spine", "5) Draft Script", "6) Validate + Fix", "7) Export"])

# Run state
if "run_id" not in st.session_state:
    st.session_state.run_id = None
if "thumbnail_brief" not in st.session_state:
    st.session_state.thumbnail_brief = None
if "case_candidates" not in st.session_state:
    st.session_state.case_candidates = None
if "chosen_case" not in st.session_state:
    st.session_state.chosen_case = None
if "fact_spine" not in st.session_state:
    st.session_state.fact_spine = None
if "script_text" not in st.session_state:
    st.session_state.script_text = None
if "acts" not in st.session_state:
    st.session_state.acts = None
if "scores" not in st.session_state:
    st.session_state.scores = None

with tabs[0]:
    st.subheader("Upload thumbnail + optional guidance")
    thumb = st.file_uploader("Thumbnail image", type=["png", "jpg", "jpeg"])
    optional_hint = st.text_area("Optional: 1–2 lines about intended vibe (optional)", "")
    if st.button("Start new run"):
        st.session_state.run_id = f"run_{int(time.time())}"
        ensure_run_dir(st.session_state.run_id)
        st.session_state.thumbnail_brief = None
        st.session_state.case_candidates = None
        st.session_state.chosen_case = None
        st.session_state.fact_spine = None
        st.session_state.script_text = None
        st.session_state.acts = None
        st.session_state.scores = None
        st.success(f"New run started: {st.session_state.run_id}")

    if thumb:
        img = Image.open(thumb).convert("RGB")
        st.image(img, caption="Thumbnail", use_column_width=True)
        st.session_state._thumb_img = img
        st.session_state._thumb_hint = optional_hint

with tabs[1]:
    st.subheader("Generate thumbnail brief (structured)")
    if st.button("Build Thumbnail Brief"):
        if not st.session_state.get("_thumb_img"):
            st.error("Upload a thumbnail in Inputs first.")
        else:
            brief = build_thumbnail_brief(st.session_state._thumb_img, st.session_state._thumb_hint)
            st.session_state.thumbnail_brief = brief
            save_json(st.session_state.run_id, "thumbnail_brief.json", brief)
            st.success("Thumbnail brief created.")
    if st.session_state.thumbnail_brief:
        st.json(st.session_state.thumbnail_brief)

with tabs[2]:
    st.subheader("Gemini research: find 3–5 real cases matching thumbnail vibe")
    if st.button("Find candidate cases (Gemini)"):
        if not has_gemini:
            st.error("Missing GEMINI_API_KEY in .env")
        elif not st.session_state.thumbnail_brief:
            st.error("Build thumbnail brief first.")
        else:
            cases = gemini_find_cases(st.session_state.thumbnail_brief)
            st.session_state.case_candidates = cases
            save_json(st.session_state.run_id, "case_candidates.json", cases)
            st.success("Candidates retrieved.")
    if st.session_state.case_candidates:
        for i, c in enumerate(st.session_state.case_candidates, start=1):
            with st.expander(f"Candidate {i}: {c.get('title','(no title)')} — confidence: {c.get('confidence','?')}"):
                st.write(c.get("summary", ""))
                st.write("Sources:")
                for s in c.get("sources", []):
                    st.write(f"- {s}")
        idx = st.number_input("Pick candidate number", min_value=1, max_value=len(st.session_state.case_candidates), value=1)
        if st.button("Select case"):
            st.session_state.chosen_case = st.session_state.case_candidates[idx-1]
            save_json(st.session_state.run_id, "chosen_case.json", st.session_state.chosen_case)
            st.success("Case selected.")

with tabs[3]:
    st.subheader("Build Fact Spine (real-case backbone + allowed fictionalization)")
    if st.button("Build Fact Spine"):
        if not st.session_state.chosen_case:
            st.error("Select a case first.")
        else:
            spine = build_fact_spine(st.session_state.chosen_case)
            st.session_state.fact_spine = spine
            save_json(st.session_state.run_id, "fact_spine.json", spine)
            st.success("Fact spine built.")
    if st.session_state.fact_spine:
        st.json(st.session_state.fact_spine)

with tabs[4]:
    st.subheader("Draft full script (one continuous draft) — Claude Opus")
    if st.button("Generate Full Script"):
        if not has_claude:
            st.error("Missing ANTHROPIC_API_KEY in .env")
        elif not st.session_state.fact_spine:
            st.error("Build the Fact Spine first.")
        else:
            script = claude_write_full_script(
                fact_spine=st.session_state.fact_spine,
                tone_preset=tone_preset,
                min_words=int(min_words),
                max_words=int(max_words),
            )
            st.session_state.script_text = script
            save_json(st.session_state.run_id, "script_meta.json", {"word_count": word_count(script)})
            st.success(f"Script generated. Words: {word_count(script)}")
    if st.session_state.script_text:
        st.text_area("Draft script (read-only here)", st.session_state.script_text, height=500)

with tabs[5]:
    st.subheader("Validate per act + patch weak blocks only")
    if st.button("Split into Acts"):
        if not st.session_state.script_text:
            st.error("Generate a script first.")
        else:
            acts = split_into_acts(st.session_state.script_text)
            st.session_state.acts = acts
            save_json(st.session_state.run_id, "acts.json", acts)
            st.success("Acts split.")
    if st.session_state.acts:
        st.write("Acts detected:", list(st.session_state.acts.keys()))
        if st.button("Score Acts (Rubric)"):
            scores = score_act_bundle(st.session_state.acts)
            st.session_state.scores = scores
            save_json(st.session_state.run_id, "scores.json", scores)
            st.success("Scored.")
        if st.session_state.scores:
            st.json(st.session_state.scores)

        if st.button("Patch weak blocks (≤3)"):
            if not has_claude:
                st.error("Need Claude API key for patch rewrite.")
            else:
                new_script, patch_log = patch_rewrite_weak_blocks(
                    full_script=st.session_state.script_text,
                    acts=st.session_state.acts,
                    scores=st.session_state.scores,
                    fact_spine=st.session_state.fact_spine,
                    tone_preset=tone_preset,
                    max_passes=int(max_fix_passes),
                )
                st.session_state.script_text = new_script
                save_json(st.session_state.run_id, "patch_log.json", patch_log)
                st.success(f"Patched. Words now: {word_count(new_script)}")

with tabs[6]:
    st.subheader("Export")
    if st.button("Export DOCX"):
        if not st.session_state.script_text:
            st.error("No script to export.")
        else:
            outpath = export_script_docx(st.session_state.run_id, st.session_state.script_text)
            st.success("Exported.")
            with open(outpath, "rb") as f:
                st.download_button("Download DOCX", f, file_name=os.path.basename(outpath))
