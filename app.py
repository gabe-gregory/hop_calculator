import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from raman_simulation import simulation as hop
import plotly.graph_objects as go

class App:
    def __init__(self):
        st.set_page_config(page_title="HOP Calculator", layout="wide")
        st.title(r"40Ca+ D5/2 high order calculator")
        
        with st.spinner("Initializing calculator..."):
            self.sim = self.initialize()
    
        self.inputs()
        self.calculate()
        tab1, tab2 = st.tabs(["Stark Shifts", "Rabi Frequencies"])
        with tab1:
            self.plot_stark_shifts()

        with tab2:
            self.plot_rabi_frequencies()

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
        self.sim.r_sp = col1.number_input(
            "spr", value=0.0, min_value=0.0, max_value=1.0,
            step=0.1, format="%.1f", label_visibility="collapsed"
        )
        self.sim.b_sp = col2.number_input(
            "spb", value=0.3, min_value=0.0, max_value=1.0,
            step=0.1, format="%.1f", label_visibility="collapsed"
        )

        # π
        label, col1, col2 = st.sidebar.columns([1, 2, 2])
        label.write("π")
        self.sim.r_pi = col1.number_input(
            "pir", value=0.0, min_value=0.0, max_value=1.0,
            step=0.1, format="%.1f", label_visibility="collapsed"
        )
        self.sim.b_pi = col2.number_input(
            "pib", value=0.3, min_value=0.0, max_value=1.0,
            step=0.1, format="%.1f", label_visibility="collapsed"
        )
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

    def plot_stark_shifts(self):
        st.subheader("a.c. Stark shifts")
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
        
    def plot_rabi_frequencies(self):

        labels = ["+5/2", "+3/2", "-1/2", "-5/2", "-3/2", "+1/2"]
        mF = np.array([2.5,1.5,-.5,-2.5,-1.5,.5])
        angles = np.pi/2-np.arange(6)*np.pi/3
        x,y = np.cos(angles),np.sin(angles)

        rabi = np.zeros((6,6))
        for i in range(6):
            for j in range(i+1,6): rabi[i,j] = i+j

        st.session_state.setdefault("rabi_transition_v3",(0,2))
        selected = st.session_state.rabi_transition_v3

        fig = go.Figure()
        fig.add_annotation(x=0,y=.15,xref="paper",yref="paper",
                           text="<b>Transition Rabi frequencies given in kHz</b>",
                           showarrow=False,font=dict(size=16))
                    
        transitions = [(i,j) for i in range(6) for j in range(i+1,6)]
        order = lambda ij: 2 if abs(mF[ij[0]]-mF[ij[1]])<=2 else 4 if abs(mF[ij[0]]-mF[ij[1]])==3 else 6
        transitions.sort(key=order)
        max_rabi = max(abs(rabi[i,j]) for i,j in transitions)

        def intersection_t(i,j,k,l):
            p,q = np.array([x[i],y[i]]),np.array([x[k],y[k]])
            r,s = np.array([x[j]-x[i],y[j]-y[i]]),np.array([x[l]-x[k],y[l]-y[k]])
            cross = lambda a,b: a[0]*b[1]-a[1]*b[0]
            den = cross(r,s)
            if abs(den)<1e-10: return None
            t,u = cross(q-p,s)/den,cross(q-p,r)/den
            return t if 1e-6<t<1-1e-6 and 1e-6<u<1-1e-6 else None

        label_positions = {}
        for i,j in transitions:
            ints = [intersection_t(i,j,k,l) for k,l in transitions if (i,j)!=(k,l)]
            ints = np.sort(np.unique(np.round([t for t in ints if t is not None],8)))
            if len(ints)>=2:
                n = np.argmax(np.diff(ints)); t = (ints[n]+ints[n+1])/2
            elif len(ints)==1: t = ints[0]/2 if ints[0]>.5 else (ints[0]+1)/2
            else: t = .5
            label_positions[i,j] = t

        hover_traces = []
        for i,j in transitions:
            value,dx,dy = rabi[i,j],x[j]-x[i],y[j]-y[i]
            photon_order = order((i,j))
            rgb = "0,0,0" if photon_order==2 else "135,206,250" if photon_order==4 else "240,128,128"
            opacity = 1 if (i,j)==selected else .25
            width = (1+6*abs(value)/max_rabi if max_rabi else 1)+2*((i,j)==selected)

            fig.add_trace(go.Scatter(
                x=[x[i],x[j]],y=[y[i],y[j]],mode="lines",
                line=dict(color=f"rgba({rgb},{opacity})",width=width),
                hoverinfo="skip",showlegend=False))

            t = label_positions[i,j]
            lx,ly = x[i]+t*dx,y[i]+t*dy

            fig.add_trace(go.Scatter(
                x=[lx],y=[ly],mode="markers",
                marker=dict(size=30,color="white"),
                hoverinfo="skip",showlegend=False))

            fig.add_annotation(
                x=lx,y=ly,text=f"{value:.2f}",showarrow=False,
                font=dict(size=11,color="black"))

            tc = np.linspace(.08,.92,30)
            hover_traces.append(go.Scatter(
                x=x[i]+tc*dx,y=y[i]+tc*dy,mode="markers",
                marker=dict(size=15,color="rgba(0,0,0,0.001)"),
                customdata=[[i,j]]*len(tc),
                hovertemplate=f"{labels[i]} ↔ {labels[j]}<br>{photon_order}-photon<br>Ω = {value:.2f} kHz<extra></extra>",
                selected=dict(marker=dict(opacity=.001)),
                unselected=dict(marker=dict(opacity=.001)),showlegend=False))

        for trace in hover_traces: fig.add_trace(trace)

        borders = ["black" if i in selected else "rgba(0,0,0,.25)" for i in range(6)]
        texts = ["black" if i in selected else "rgba(0,0,0,.25)" for i in range(6)]

        fig.add_trace(go.Scatter(
            x=x,y=y,mode="markers+text",
            marker=dict(size=65,color="white",line=dict(color=borders,width=2)),
            text=labels,textposition="middle center",textfont=dict(size=16,color=texts),
            hoverinfo="skip",showlegend=False))

        for name,color in [("2-photon","black"),("4-photon","lightskyblue"),("6-photon","lightcoral")]:
            fig.add_trace(go.Scatter(
                x=[None],y=[None],mode="lines",line=dict(color=color,width=4),
                name=name,hoverinfo="skip",showlegend=True))

        fig.update_layout(
            height=700,margin=dict(l=20,r=20,t=20,b=20),
            xaxis=dict(visible=False,range=[-1.35,1.35],scaleanchor="y",scaleratio=1),
            yaxis=dict(visible=False,range=[-1.25,1.25]),
            plot_bgcolor="white",clickmode="event+select",showlegend=True,
            legend=dict(x=.1,y=.8,xanchor="left",yanchor="top",
                        bgcolor="rgba(255,255,255,.8)"))

        event = st.plotly_chart(
            fig,use_container_width=True,key="rabi_diagram_v3",
            on_select="rerun",selection_mode="points")

        if event and event.selection.points:
            data = event.selection.points[-1].get("customdata")
            if data is not None:
                new_selected = tuple(map(int,data))
                if new_selected != selected:
                    st.session_state.rabi_transition_v3 = new_selected
                    st.rerun()

        i,j = st.session_state.rabi_transition_v3
        
            
if __name__ == "__main__":
    App()
