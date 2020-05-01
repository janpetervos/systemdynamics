import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ipywidgets as widgets
from ipywidgets import VBox
from IPython.display import display

# instellen opmaak visualisaties
sns.set(style='whitegrid', rc={"figure.figsize": (10, 5), "lines.linewidth": 2.5}, font="Arial", font_scale=1.2)
kleur = ["#EC5D57", "#51A7F9", "#70BF41", "#F39019", "#F5D327", "#AA64D6"]  # rood, groen, blauw, oranje, geel, paars
sns.set_palette(kleur)

# bepalen tijdsinstellingen
dt = 0.5 ** 6  # [jaar] tijdstap numerieke integratie
begintijd = 2020  # het jaar waarmee de simulatie begint
eindtijd = 2050  # [jaar] eindtijd simulatie
n = int((eindtijd - begintijd) / dt)  # aantal integratiestappen
t = np.linspace(begintijd, eindtijd, n)  # tijdsvector integratieproces


def Euler(f, x0, t, args=None):  # integrator
    n = len(t)
    x = np.array([x0] * n)
    for i in range(n - 1):
        h = t[i + 1] - t[i]
        x[i + 1] = x[i] + h * f(x[i], t[i], args)
    return x.T


def S(stocks, t, args):  # systeem
    
    # uitpakken parameters
    CEM_I, CEM_III, GP, Fines, \
    intro_CEM_I, intro_CEM_III, intro_GP, intro_Fines, \
    minimale_emissie_CEM_I, minimale_emissie_CEM_III, minimale_emissie_GP, minimale_emissie_Fines, \
    tijdconstante_CEM_I, tijdconstante_CEM_III, tijdconstante_GP, tijdconstante_Fines, \
    transitietijd_CEM_I, transitietijd_CEM_III, transitietijd_GP, transitietijd_Fines = args

    # uitpakken "stocks"
    emissie_CEM_I, emissie_CEM_III, emissie_GP, emissie_Fines, \
    fractie_CEM_I, fractie_CEM_III, fractie_GP, fractie_Fines = stocks

    # corrigeren voor uitgeschakelde bindmiddelen
    if not CEM_I:
        verandering_emissie_CEM_I = 0.0
        emissiefactor_CEM_I = 0.0
        reductiepotentieel_CEM_I = 0.0
    if not CEM_III:
        verandering_emissie_CEM_III = 0.0
        emissiefactor_CEM_III = 0.0
        reductiepotentieel_CEM_III = 0.0
    if not GP:
        verandering_emissie_GP = 0.0
        emissiefactor_GP = 0.0
        reductiepotentieel_GP = 0.0
    if not Fines:
        verandering_emissie_Fines = 0.0
        emissiefactor_Fines = 0.0
        reductiepotentieel_Fines = 0.0

    # berekenen "flows" emissies van de bindmiddelen
    tijd = t * dt + begintijd
    if CEM_I:
        if tijd <= intro_CEM_I:
            verandering_emissie_CEM_I = 0.0
        else:
            afnamepotentieel_CEM_I = (initiele_emissie_CEM_I - minimale_emissie_CEM_I - emissie_CEM_I) / (
                    initiele_emissie_CEM_I - minimale_emissie_CEM_I)
        verandering_emissie_CEM_I = emissie_CEM_I * afnamepotentieel_CEM_I / tijdconstante_CEM_I
    if CEM_III:
        if tijd <= intro_CEM_III:
            verandering_emissie_CEM_III = 0.0
        else:
            afnamepotentieel_CEM_III = (initiele_emissie_CEM_III - minimale_emissie_CEM_III - emissie_CEM_III) / (
                    initiele_emissie_CEM_III - minimale_emissie_CEM_III)
            verandering_emissie_CEM_III = emissie_CEM_III * afnamepotentieel_CEM_III / tijdconstante_CEM_III
    if GP:
        if tijd <= intro_GP:
            verandering_emissie_GP = 0.0
        else:
            afnamepotentieel_GP = (initiele_emissie_GP - minimale_emissie_GP - emissie_GP) / (
                    initiele_emissie_GP - minimale_emissie_GP)
            verandering_emissie_GP = emissie_GP * afnamepotentieel_GP / tijdconstante_GP
    if Fines:
        if tijd <= intro_Fines:
            verandering_emissie_Fines = 0.0
        else:
            afnamepotentieel_Fines = (initiele_emissie_Fines - minimale_emissie_Fines - emissie_Fines) / (
                    initiele_emissie_Fines - minimale_emissie_Fines)
            verandering_emissie_Fines = emissie_Fines * afnamepotentieel_Fines / tijdconstante_Fines

    # bepalen emissiefactor per bindmiddel
    if CEM_I:
        emissiefactor_CEM_I = initiele_emissie_CEM_I - emissie_CEM_I
    if CEM_III:
        emissiefactor_CEM_III = initiele_emissie_CEM_III - emissie_CEM_III
    if GP:
        emissiefactor_GP = initiele_emissie_GP - emissie_GP
    if Fines:
        emissiefactor_Fines = initiele_emissie_Fines - emissie_Fines

    # bepalen emissiereductiepotentieel per bindmiddel
    emissies_gemiddeld = (emissiefactor_CEM_I + emissiefactor_CEM_III + emissiefactor_GP + emissiefactor_Fines) / (
            CEM_I + CEM_III + GP + Fines)
    if CEM_I:
        reductiepotentieel_CEM_I = (emissies_gemiddeld - emissiefactor_CEM_I) / emissies_gemiddeld
    if CEM_III:
        reductiepotentieel_CEM_III = (emissies_gemiddeld - emissiefactor_CEM_III) / emissies_gemiddeld
    if GP:
        reductiepotentieel_GP = (emissies_gemiddeld - emissiefactor_GP) / emissies_gemiddeld
    if Fines:
        reductiepotentieel_Fines = (emissies_gemiddeld - emissiefactor_Fines) / emissies_gemiddeld

    # berekenen "flows" fracties van de bindmiddelen
    verandering_fractie_CEM_I = fractie_CEM_I * reductiepotentieel_CEM_I / transitietijd_CEM_I
    verandering_fractie_CEM_III = fractie_CEM_III * reductiepotentieel_CEM_III / transitietijd_CEM_III
    verandering_fractie_GP = fractie_GP * reductiepotentieel_GP / transitietijd_GP
    verandering_fractie_Fines = fractie_Fines * reductiepotentieel_Fines / transitietijd_Fines

    return np.array([verandering_emissie_CEM_I, verandering_emissie_CEM_III, verandering_emissie_GP,
                     verandering_emissie_Fines, verandering_fractie_CEM_I, verandering_fractie_CEM_III,
                     verandering_fractie_GP, verandering_fractie_Fines])


""" beginvoorwaarden emissie_CEM_I, emissie_CEM_III, emissie_GP, emissie_Fines,
    fractie_CEM_I, fractie_CEM_III, fractie_GP en fractie_Fines """
S0 = [0.01, 0.01, 0.01, 0.01, 0.69, 0.3, 0.01, 0.02]

# tijdconstanten en parameters
initiele_emissie_CEM_I = 0.8
initiele_emissie_CEM_III = 0.5
initiele_emissie_GP = 0.05
initiele_emissie_Fines = 0.3

# interface voor aan- of uitzetten van bindmiddelen
CEM_I_button = widgets.Checkbox(
    value=True,
    description="CEM-I",
    icon='check')
CEM_III_button = widgets.Checkbox(
    value=True,
    description="CEM-III",
    icon='check')
GP_button = widgets.Checkbox(
    value=True,
    description="GP",
    icon='check')
Fines_button = widgets.Checkbox(
    value=True,
    description="Fines",
    icon='check')

# interface voor de introductie van emissiereductie
IT_CEM_I_slider = widgets.IntSlider(
    value=begintijd,
    min=begintijd,
    max=eindtijd,
    step=1,
    description="CEM-I",
    readout_format="d")
IT_CEM_III_slider = widgets.IntSlider(
    value=begintijd,
    min=begintijd,
    max=eindtijd,
    step=1,
    description="CEM-III",
    readout_format="d")
IT_GP_slider = widgets.IntSlider(
    value=begintijd,
    min=begintijd,
    max=eindtijd,
    step=1,
    description="GP",
    readout_format="d")
IT_Fines_slider = widgets.IntSlider(
    value=begintijd,
    min=begintijd,
    max=eindtijd,
    step=1,
    description="Fines",
    readout_format="d")

# interface voor de emissiefracties
CEM_I_slider = widgets.FloatSlider(
    value=0.2,
    min=0.01,
    max=0.2,
    step=0.01,
    description="CEM-I",
    readout_format="0.2f")
CEM_III_slider = widgets.FloatSlider(
    value=0.2,
    min=0.01,
    max=0.2,
    step=0.01,
    description="CEM-III",
    readout_format="0.2f")
GP_slider = widgets.FloatSlider(
    value=0.04,
    min=0.01,
    max=0.05,
    step=0.01,
    description="GP",
    readout_format="0.2f")
Fines_slider = widgets.FloatSlider(
    value=0.04,
    min=0.01,
    max=0.05,
    step=0.01,
    description="Fines",
    readout_format="0.2f")

# interface voor de tijdconstanten emissiereductie
TC_CEM_I_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="CEM-I",
    readout_format="d")
TC_CEM_III_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="CEM-III",
    readout_format="d")
TC_GP_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="GP",
    readout_format="d")
TC_Fines_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="Fines",
    readout_format="d")

# interface voor de transitietijden
TT_CEM_I_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="CEM-I",
    readout_format="d")
TT_CEM_III_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="CEM-III",
    readout_format="d")
TT_GP_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="GP",
    readout_format="d")
TT_Fines_slider = widgets.IntSlider(
    value=5,
    min=1,
    max=eindtijd-begintijd,
    step=1,
    description="Fines",
    readout_format="d")

# instellen user interface
tab1 = VBox(children=[CEM_I_button, CEM_III_button, GP_button, Fines_button])
tab2 = VBox(children=[IT_CEM_I_slider, IT_CEM_III_slider, IT_GP_slider, IT_Fines_slider])
tab3 = VBox(children=[CEM_I_slider, CEM_III_slider, GP_slider, Fines_slider])
tab4 = VBox(children=[TC_CEM_I_slider, TC_CEM_III_slider, TC_GP_slider, TC_Fines_slider])
tab5 = VBox(children=[TT_CEM_I_slider, TT_CEM_III_slider, TT_GP_slider, TT_Fines_slider])
tab = widgets.Tab(children=[tab1, tab2, tab3, tab4, tab5])
tab.set_title(0, "Bindmiddelen")
tab.set_title(1, "Reductiestart [jaar]")
tab.set_title(2, "Minima [tonCO2/ton]")
tab.set_title(3, "Reductietijden [jaar]")
tab.set_title(4, "Transitietijden [jaar]")
display(tab)


# uitvoeren simulatie en visualiseren resultaten
@widgets.interact_manual()
def plot():
    CEM_I = CEM_I_button.value
    CEM_III = CEM_III_button.value
    GP = GP_button.value
    Fines = Fines_button.value
    intro_CEM_I = IT_CEM_I_slider.value
    intro_CEM_III = IT_CEM_III_slider.value
    intro_GP = IT_GP_slider.value
    intro_Fines = IT_Fines_slider.value
    minimale_emissie_CEM_I = CEM_I_slider.value
    minimale_emissie_CEM_III = CEM_III_slider.value
    minimale_emissie_GP = GP_slider.value
    minimale_emissie_Fines = GP_slider.value
    tijdconstante_CEM_I = TC_CEM_I_slider.value
    tijdconstante_CEM_III = TC_CEM_III_slider.value
    tijdconstante_GP = TC_GP_slider.value
    tijdconstante_Fines = TC_Fines_slider.value
    transitietijd_CEM_I = TT_CEM_I_slider.value
    transitietijd_CEM_III = TT_CEM_III_slider.value
    transitietijd_GP = TT_GP_slider.value
    transitietijd_Fines = TT_Fines_slider.value
    parameters = (CEM_I, CEM_III, GP, Fines, \
                  intro_CEM_I, intro_CEM_III, intro_GP, intro_Fines, \
                  minimale_emissie_CEM_I, minimale_emissie_CEM_III, minimale_emissie_GP, minimale_emissie_Fines, \
                  tijdconstante_CEM_I, tijdconstante_CEM_III, tijdconstante_GP, tijdconstante_Fines, \
                  transitietijd_CEM_I, transitietijd_CEM_III, transitietijd_GP, transitietijd_Fines)
    stocks = Euler(S, S0, t, args=parameters)
    emissie_CEM_I, emissie_CEM_III, emissie_GP, emissie_Fines, \
    fractie_CEM_I, fractie_CEM_III, fractie_GP, fractie_Fines = stocks

    # bewerken resultaten
    emissiefactor_CEM_I = initiele_emissie_CEM_I - emissie_CEM_I
    emissiefactor_CEM_III = initiele_emissie_CEM_III - emissie_CEM_III
    emissiefactor_GP = initiele_emissie_GP - emissie_GP
    emissiefactor_Fines = initiele_emissie_Fines - emissie_Fines
    correctiefactor_bindmiddelen = 1 / (fractie_CEM_I + fractie_CEM_III + fractie_GP + fractie_Fines)
    fractie_CEM_I = fractie_CEM_I * correctiefactor_bindmiddelen
    fractie_CEM_III = fractie_CEM_III * correctiefactor_bindmiddelen
    fractie_GP = fractie_GP * correctiefactor_bindmiddelen
    fractie_Fines = fractie_Fines * correctiefactor_bindmiddelen
    totale_emissiefactor = emissiefactor_CEM_I * fractie_CEM_I + emissiefactor_CEM_III * fractie_CEM_III + \
                           emissiefactor_GP * fractie_GP + emissiefactor_Fines * fractie_Fines

    # visualiseren resultaten
    fig, ax = plt.subplots(3, 1, figsize=(8, 12), sharex="all")
    if CEM_I:
        ax[0].plot(t, emissiefactor_CEM_I, label="CEM-I")
        ax[2].plot(t, fractie_CEM_I, label="CEM-I")
    if CEM_III:
        ax[0].plot(t, emissiefactor_CEM_III, label="CEM-III")
        ax[2].plot(t, fractie_CEM_III, label="CEM-III")
    if GP:
        ax[0].plot(t, emissiefactor_GP, label="Geopolymeer")
        ax[2].plot(t, fractie_GP, label="Geopolymeer")
    if Fines:
        ax[0].plot(t, emissiefactor_Fines, label="Fines")
        ax[2].plot(t, fractie_Fines, label="Fines")
    ax[1].plot(t, totale_emissiefactor, label="Totale emissiefactor")
    ax[0].set_title("Tijdverloop emissie bindmiddelen", fontweight="bold")
    ax[1].set_title("Tijdverloop totale emissie bindmiddelen", fontweight="bold")
    ax[2].set_title("Tijdverloop fracties bindmiddelen", fontweight="bold")
    ax[2].set_xlabel("Tijd [jaar]")
    ax[0].set_ylabel("Emissiefracties [tonCO2/ton]")
    ax[1].set_ylabel("Emissiefractie [dmnl]")
    ax[2].set_ylabel("Bindmiddelenfracties [dmnl]")
    ax[0].set_ylim(-0.05, 1.05)
    ax[1].set_ylim(-0.05, 1.05)
    ax[2].set_ylim(-0.05, 1.05)
    ax[0].legend(loc="best")
    ax[1].legend(loc="best")
    ax[2].legend(loc="best", ncol=2)
    # plt.tight_layout()
    # plt.show()

    # beschikbaar maken emissiefracties buiten python-functie
    global emissies, fracties
    emissies = [emissiefactor_CEM_I, emissiefactor_CEM_III, emissiefactor_GP, emissiefactor_Fines]
    fracties = [fractie_CEM_I, fractie_CEM_III, fractie_GP, fractie_Fines]
