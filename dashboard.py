import streamlit as st

from src.app import run_firewall


st.set_page_config(
    page_title="AI Output Firewall",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ AI Output Quality & Hallucination Firewall")
st.caption("Generate or submit an LLM answer, verify its claims against trusted evidence, and inspect the firewall decision.")

with st.sidebar:
    st.header("Firewall")
    st.write("**PASS** ≥ 80")
    st.write("**WARN** 50–79")
    st.write("**REJECT** < 50")
    st.divider()
    st.write("When `BEDROCK_KNOWLEDGE_BASE_ID` is configured, evidence is retrieved from Amazon Bedrock Knowledge Bases. Otherwise the local demo evidence is used.")

question = st.text_area(
    "Question",
    value="What encryption does Amazon S3 support?",
    height=90,
)

mode = st.radio(
    "Answer source",
    ["Generate with Amazon Bedrock", "Verify a supplied answer"],
    horizontal=True,
)

supplied_answer = ""
if mode == "Verify a supplied answer":
    supplied_answer = st.text_area(
        "Candidate answer",
        placeholder="Paste an LLM answer here to test it...",
        height=140,
    )

if st.button("Run Firewall", type="primary", use_container_width=True):
    if not question.strip():
        st.warning("Enter a question first.")
    elif mode == "Verify a supplied answer" and not supplied_answer.strip():
        st.warning("Enter a candidate answer first.")
    else:
        try:
            answer_arg = supplied_answer if mode == "Verify a supplied answer" else None
            answer, result, evidence = run_firewall(question.strip(), answer_arg)

            st.subheader("Firewall Decision")
            score_col, decision_col, supported_col, unsupported_col = st.columns(4)
            score_col.metric("Quality score", f"{result.score}/100")
            decision_col.metric("Decision", result.decision)
            supported_col.metric("Supported claims", result.supported_claims)
            unsupported_col.metric("Unsupported claims", result.unsupported_claims)

            if result.decision == "PASS":
                st.success("PASS — the answer met the current evidence-support threshold.")
            elif result.decision == "WARN":
                st.warning("WARN — some claims may need stronger evidence or review.")
            else:
                st.error("REJECT — the answer did not meet the minimum evidence-support threshold.")

            st.subheader("Candidate Answer")
            st.write(answer)

            st.subheader("Claim Analysis")
            if result.claims:
                rows = [
                    {
                        "Claim": claim.claim,
                        "Support": f"{claim.support_score * 100:.1f}%",
                        "Supported": "Yes" if claim.supported else "No",
                    }
                    for claim in result.claims
                ]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.info("No claims were extracted from the answer.")

            st.subheader("Retrieved Evidence")
            for index, item in enumerate(evidence, start=1):
                source = item.source_uri or "Unknown source"
                relevance = f" — relevance {item.relevance_score:.3f}" if item.relevance_score is not None else ""
                with st.expander(f"Evidence {index}: {source}{relevance}"):
                    st.write(item.text)

        except Exception as exc:
            st.error(f"Firewall execution failed: {exc}")
            st.info("For live generation, verify AWS credentials, Bedrock model access, region, and IAM permissions. You can still use supplied-answer mode for local verification.")

st.divider()
st.caption("Portfolio project: AWS + Amazon Bedrock + evidence-backed LLM verification")
