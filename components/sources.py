from __future__ import annotations
import streamlit as st


def render(data: dict) -> None:
    st.markdown('<div class="as-section">10 &nbsp; Evidence &amp; Sources</div>', unsafe_allow_html=True)

    sources = data.get("sources", []) or []
    total   = len(sources)

    with st.expander(f"View all {total} source URL{'s' if total != 1 else ''}", expanded=False):
        if not sources:
            st.markdown('<div class="as-empty">No sources recorded.</div>', unsafe_allow_html=True)
            return

        filter_text = st.text_input("Filter sources", placeholder="e.g. security, github, nvd", label_visibility="collapsed")
        filtered = [s for s in sources if filter_text.lower() in s.lower()] if filter_text else sources

        st.markdown(f'<div style="font-size:0.7rem;color:#64748b;margin-bottom:0.5rem">'
                    f'Showing {len(filtered)} of {total}</div>', unsafe_allow_html=True)

        for url in filtered:
            st.markdown(f'<a class="as-src" href="{url}" target="_blank">{url}</a>', unsafe_allow_html=True)

        # Copy-all helper
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="Download source list (.txt)",
            data="\n".join(filtered),
            file_name="agentshield_sources.txt",
            mime="text/plain",
            use_container_width=True,
        )
