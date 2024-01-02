import Processors.Data_reader as d_r
import Processors.rule_1
import Processors.rule_2
import Processors.rule_3
import Processors.rule_4
import Processors.rule_5
import Processors.rule_6
import Processors.rule_7
import Processors.rule_8
import Processors.rule_9
import Processors.rule_10
import Processors.rule_11
import Processors.app
import Processors.gpt
import streamlit as st

def start_func():
    # Einlesen der Modelle
    model_paths = d_r.read_data()

    if model_paths is not None:
        # Vorprüfung
        rule_1 = Processors.rule_1.r1(model_paths)
        rule_2 = Processors.rule_2.r2(model_paths)
        rule_3 = Processors.rule_3.r3(model_paths)
        rule_4 = Processors.rule_4.r4(model_paths)
        rule_5 = Processors.rule_5.r5(model_paths)
        rule_6 = Processors.rule_6.r6(model_paths)
        rule_7 = Processors.rule_7.r7(model_paths)
        rule_8 = Processors.rule_8.r8(model_paths)
        rule_9 = Processors.rule_9.r9(model_paths)
        rule_10 = Processors.rule_10.r10(model_paths)
        rule_11 = Processors.rule_11.r11(model_paths)

        # Prüfungsbericht
        st.header("Der Vorprüfungsbericht steht bereit!")
        tab1, tab2 = st.tabs(["Dashboard", "KI-Assistent"])

        with tab1:
            db = Processors.app.dashboard()
            pass

        with tab2:
            gpt = Processors.gpt.gpt()
            pass

    else:
        return None

if __name__ == "__main__":
    start_func()