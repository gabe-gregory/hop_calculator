import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from raman_simulation import simulation as hop
import plotly.graph_objects as go

class App:
    def __init__(self):
        st.set_page_config(page_title="HOP Calculator", layout="wide")
        st.title(r"$^{40}Ca^+ D_{5/2} a.c. Stark shift calculator$")
        
        with st.spinner("Initializing calculator..."):
            self.sim = self.initialize()
    
        self.inputs()
        self.calculate()
        self.plot()

    @st.cache_resource
    def initialize(_self):
        sim = hop.sim(ls_order=8)
        sim.get_f()
        return sim  
        
    def inputs(self):
        st.sidebar.header("Parameters")

        # Column titles
        label, col1, col2 = st.sidebar.columns([1, 2, 2])
        col1.markdown("**Beam 1**")
        col2.markdown("**Beam 2**")

        # Power
        label, col1, col2 = st.sidebar.columns([1, 2, 2])
        label.write("Power")
        # self.sim.Pr = col1.number_input("Pr", value=100.0, label_visibility="collapsed")*1e-3
        # self.sim.Pb = col2.number_input("Pb", value=100.0, label_visibility="collapsed")*1e-3
        self.sim.Pr = col1.slider(
            "Pr",
            min_value=0.0,
            max_value=300.0,
            value=100.0,
            step=1.0,
            label_visibility="collapsed"
        )*1e-3

        self.sim.Pb = col2.slider(
            "Pb",
            min_value=0.0,
            max_value=300.0,
            value=100.0,
            step=1.0,
            label_visibility="collapsed"
        )*1e-3
        # σ+
        label, col1, col2 = st.sidebar.columns([1, 2, 2])
        label.write("σ+")
        self.sim.r_sp = col1.number_input("spr", value=0.0, label_visibility="collapsed")
        self.sim.b_sp = col2.number_input("spb", value=1/3, label_visibility="collapsed")

        # π
        label, col1, col2 = st.sidebar.columns([1, 2, 2])
        label.write("π")
        self.sim.r_pi = col1.number_input("pir", value=0.0, label_visibility="collapsed")
        self.sim.b_pi = col2.number_input("pib", value=1/3, label_visibility="collapsed")

        # σ− (calculated)
        self.sim.r_sm = 1 - self.sim.r_sp - self.sim.r_pi
        self.sim.b_sm = 1 - self.sim.b_sp - self.sim.b_pi

        label, col1, col2 = st.sidebar.columns([1, 2, 2])
        label.write("σ−")
        col1.write(f"{self.sim.r_sm:.2f}")
        col2.write(f"{self.sim.b_sm:.2f}")
        
        # Additional parameters
        st.sidebar.divider()

        self.sim.ω = st.sidebar.slider(
            "Beam detuning (MHz)",
            min_value=-20.0,
            max_value=20.0,
            value=5.0,
            step=0.1
        )*2*np.pi*1e6
        
        self.sim.Δ = st.sidebar.number_input("P state detuning (THz)", value=-44)*2*np.pi*1e12
        self.sim.ω0 = st.sidebar.number_input("Zeeman splitting (MHz)", value=2.63)*2*np.pi*1e6
        
        self.sim.get_rabi_frequencies()
        
    def calculate(self):
        self.sim.analytics([self.sim.Pb])
        
        
        
        
        self.x = self.sim.RID_rpi
        self.y = self.sim.tpi_4

    def plot(self):

        labels = ["+5/2", "+3/2", "+1/2", "-1/2", "-3/2", "-5/2"]

        colors = {
            2: "gray",
            4: "gray",
            6: "gray",
            8: "gray"
        }
        
        titles = {
            2: "black",
            4: "black",
            6: "black",
            8: "black"
        }

        def make_fig(values, title, color):
            fig = go.Figure()

            fig.add_bar(
                x=labels,
                y=values,
                marker_color=color,
                hovertemplate="%{y:.2f} kHz<extra></extra>"
            )

            fig.update_layout(
                xaxis_title="",
                yaxis_title="a.c. Stark shift (kHz)",
                title=dict(
                    text=f"<b>{title}</b>",
                    font=dict(color='black')
                ),
                showlegend=False
            )

            return fig

        # Plot 1
        values2 = np.array([
            self.sim.δ02_bank[0],
            self.sim.δ12_bank[0],
            self.sim.δ22_bank[0],
            self.sim.δ32_bank[0],
            self.sim.δ42_bank[0],
            self.sim.δ52_bank[0]])/(2*np.pi*1e3)

        # Plot 2
        values4 = np.array([
            self.sim.δ04_bank[0],
            self.sim.δ14_bank[0],
            self.sim.δ24_bank[0],
            self.sim.δ34_bank[0],
            self.sim.δ44_bank[0],
            self.sim.δ54_bank[0]])/(2*np.pi*1e3)

        # Plot 3
        values6 = np.array([
            self.sim.δ06_bank[0],
            self.sim.δ16_bank[0],
            self.sim.δ26_bank[0],
            self.sim.δ36_bank[0],
            self.sim.δ46_bank[0],
            self.sim.δ56_bank[0]])/(2*np.pi*1e3)

        # Plot 4
        values8 = np.array([
            self.sim.δ08_bank[0],
            self.sim.δ18_bank[0],
            self.sim.δ28_bank[0],
            self.sim.δ38_bank[0],
            self.sim.δ48_bank[0],
            self.sim.δ58_bank[0]])/(2*np.pi*1e3)

        # 2 x 2 grid
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(make_fig(values2, "2nd order", colors[2]))

        with col2:
            st.plotly_chart(make_fig(values4, "4th order", colors[4]))

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(make_fig(values6, "6th order", colors[6]))

        with col2:
            st.plotly_chart(make_fig(values8, "8th order", colors[8]))
        
#     def plot(self):

#         labels = ["+5/2", "+3/2", "+1/2", "-1/2", "-3/2", "-5/2"]

#         def make_fig(values, title):
#             fig = go.Figure()

#             fig.add_bar(
#                 x=labels,
#                 y=values,
#                 hovertemplate="%{y:.2f} kHz<extra></extra>"
#             )

#             fig.update_layout(
#                 xaxis_title="",
#                 yaxis_title="a.c. Stark shift (kHz)",
#                 title=title,
#                 showlegend=False
#             )

#             return fig

#         # Plot 1
#         values2 = np.array([
#             self.sim.δ02_bank[0],
#             self.sim.δ12_bank[0],
#             self.sim.δ22_bank[0],
#             self.sim.δ32_bank[0],
#             self.sim.δ42_bank[0],
#             self.sim.δ52_bank[0]])/(2*np.pi*1e3)


#         # Plot 2
#         values4 = np.array([
#             self.sim.δ04_bank[0],
#             self.sim.δ14_bank[0],
#             self.sim.δ24_bank[0],
#             self.sim.δ34_bank[0],
#             self.sim.δ44_bank[0],
#             self.sim.δ54_bank[0]])/(2*np.pi*1e3)

#         # Plot 3
#         values6 = np.array([
#             self.sim.δ06_bank[0],
#             self.sim.δ16_bank[0],
#             self.sim.δ26_bank[0],
#             self.sim.δ36_bank[0],
#             self.sim.δ46_bank[0],
#             self.sim.δ56_bank[0]])/(2*np.pi*1e3)

#         # Plot 4
#         values8 = np.array([
#             self.sim.δ08_bank[0],
#             self.sim.δ18_bank[0],
#             self.sim.δ28_bank[0],
#             self.sim.δ38_bank[0],
#             self.sim.δ48_bank[0],
#             self.sim.δ58_bank[0]])/(2*np.pi*1e3)

#         # 2 x 2 grid
#         col1, col2 = st.columns(2)

#         with col1:
#             st.plotly_chart(make_fig(values2, "2nd order"))

#         with col2:
#             st.plotly_chart(make_fig(values4, "4th order"))

#         col1, col2 = st.columns(2)

#         with col1:
#             st.plotly_chart(make_fig(values6, "6th order"))

#         with col2:
#             st.plotly_chart(make_fig(values8, "8th order"))

if __name__ == "__main__":
    App()
