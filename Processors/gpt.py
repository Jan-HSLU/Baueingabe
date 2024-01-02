from openai import OpenAI
import streamlit as st
import Helpers.Data_Helpers as hlp

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def gpt():
    prompt = st.text_input("Fragen zur Vorprüfung an den Systemassistent hier eintippen:")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    ub = hlp.Umbauter_Raum.all_instances.values()
    ub_str = [str(obj) for obj in ub]
    gf = hlp.Geschossfläche.get_instances()
    gf_str = [str(obj) for obj in gf]
    uz = hlp.Überbauungsziffer.get_uez()
    sia = hlp.SIA_416.get_all_instances()
    sia_str = [str(obj) for obj in sia]
    gw = hlp.Wohnungsmix.get_gesamtzahl_aller_wohnungen()
    wm = hlp.Wohnungsmix.get_all_instances()
    wm_str = [str(obj) for obj in wm]
    ppa_ist = hlp.Parkplatz._instance.ppa_ist
    ppa_soll = hlp.Parkplatz._instance.ppa_soll
    ppv_ist = hlp.Parkplatz._instance.ppv_ist
    ppv_soll = hlp.Parkplatz._instance.ppv_soll
    ff = hlp.Fensteranteil.get_instances()
    rh = hlp.Raumhöhe.get_instances()
    ga = hlp.Grenzabstand.get_instances()
    hb = hlp.Höhenbegrenzung.get_instances()


    context = (f"Die Vorprüfung des Baugesuches hat folgendes ergeben:\n"
               f"Die einzelnen Gebäude im Projekt weisen folgenden Umbauten Raum auf:\n"
               f"{ub_str}\n"
               f"Die einzelnen Gebäude im Projekt weisen folgende Geschossflächen auf:\n"
               f"{gf_str}\n"
               f"Das Projekt weist über die ganze Parzelle hinweg folgende Überbauungsziffer auf:\n"
               f"{uz}\n"
               f"Die Auswertung der Flächen nach SIA-416 im Projekt hat folgendes ergeben:\n"
               f"{sia_str}\n"
               f"Im ganzen Projekt sind wie folgt viele Wohnungen geplant:\n"
               f"{gw}\n"
               f"Eine Auswertung des Wohnungsmixes im Projekt hat folgenden hat Wohnungsspiegel ergeben:\n"
               f"{wm_str}\n"
               f"Im ganzen Projekt wurden Velo- und Autoparkplätze ermittel:\n"
               f"Auto ist:{ppa_ist}, Auto soll:{ppa_soll}, Velo ist:{ppv_ist}, Velo soll:{ppv_soll}\n"
               f"Im Folgenden wurde das Baurecht noch gerpüft:\n"
               f"Folgende Elemente haben die geltenden mindestanforderungen für Fensterflächen nicht eingehalten. Das Reglement sieht in Wohnräumen 10% der Raumfläche vor:\n"
               f"{ff}\n"
               f"Folgende Elemente haben die geltenden mindestanforderungen für Raumhöhen nicht eingehalten. Das Reglement sieht in Wohnräumen eine Mindesthöhe von 210cm vor:\n"
               f"{rh}\n"
               f"Folgende Elemente haben die geltenden Grenzabstände unterschritten:\n"
               f"{ga}\n"
               f"Folgende Elemente haben die geltenden Höhenbegrenzungen überschritten:\n"
               f"{hb}\n"
               f"Halte dich in den Antworten kurz und prägnant."
               )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def send_to_model(prompt):
        combined_prompt = context + "\n\n" + prompt
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": combined_prompt},
            ],
            max_tokens=150,
            temperature=0.5,
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
        return full_response

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = send_to_model(prompt)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    return None