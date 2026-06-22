# CorrosionLab 🧪 | High-Temperature Oxidation Kinetics Analyzer

[🇬🇧 English](#-english-version) | [🇵🇱 Polski](#-wersja-polska)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License: MIT](https://img.shields.io/badge/Code_License-MIT-green)
![License: CC BY 4.0](https://img.shields.io/badge/Data_License-CC_BY_4.0-lightgrey)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B)](https://corrosion-lab.streamlit.app)

---

## 🇬🇧 English Version

### About the Project

**CorrosionLab** is a Data Science web application designed to automate the analysis of high-temperature corrosion kinetics. It was developed to evaluate the protective performance of sol-gel nanocomposite ceramic coatings (doped with ZrO2, Y2O3, CeO2, SiO2, Al2O3) applied on FeCrAl resistance alloys.

The app serves as a modern, digital extension of a Master's Thesis defended in 2015 at the Wrocław University of Science and Technology. By transforming raw empirical data and manual calculations into a functional software tool, CorrosionLab bridges the gap between traditional materials engineering and modern Materials Informatics.

### Key Features

1. 📈 **Kinetics & Gravimetry Engine:** Automatically calculates relative mass change ($\Delta m/m_0$), scale thickness ($h$), and the parabolic oxidation rate constant ($k_p$) based on Tammann's law.
2. ⚠️ **Spallation Anomaly Detection:** Analyzes the derivative of the mass change curve to detect sudden mass drops, automatically flagging points of thermal shock or scale spallation.
3. 📉 **Predictive Curve Fitting:** Uses non-linear regression to fit kinetic models (linear, parabolic) and extrapolates future coating behavior beyond the actual experimental timeframe.
4. 🧠 **Coating Recommender System:** A rule-based expert system that recommends the optimal sol-gel coating composition (e.g., precursor type, dopant, number of layers) based on the user's specific environmental requirements.

### Language / UI Localization

The running app supports **Polish** and **English**:

* On first load, the UI language is detected from your browser locale (`st.context.locale`).
* Use the **Language** selector at the top of the sidebar to switch between Polski and English for the current session.
* Translation catalogs live in `corrosionlab/locales/` (`pl.json`, `en.json`).

Requires **Streamlit ≥ 1.37**.

### Tech Stack

* **Language:** Python
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Data Processing:** Pandas, NumPy
* **Scientific Computing:** SciPy (`scipy.optimize.curve_fit`)
* **Visualization:** Plotly

### Live Demo

You can try CorrosionLab without installing anything locally. The app is hosted on Streamlit Community Cloud:

**[https://corrosion-lab.streamlit.app](https://corrosion-lab.streamlit.app)**

### Installation & Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/YourUsername/CorrosionLab.git
   cd CorrosionLab
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:

   ```bash
   streamlit run app.py
   ```

### Data Schema

The app expects a simple `.csv` file format for oxidation data (Time vs. Mass for different samples). Example:

| time_h | TM_Control | TM1A | TM1B | TM4B |
|--------|------------|------|------|------|
| 0 | 0.01466 | 0.01500 | 0.01475 | 0.01212 |
| 12 | 0.01474 | 0.01514 | 0.01479 | 0.01204 |

### License & Citation

This repository is dual-licensed:

* **Software / Code:** Licensed under the MIT License.
* **Thesis Document & Empirical Data:** The original thesis PDF and dataset are licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).

**Citation:**

Miller, T. (2015). *Nanokompozytowe powłoki ceramiczne otrzymywane metodą zol-żel*. Master's Thesis. Faculty of Chemistry, Wrocław University of Science and Technology.

---

## 🇵🇱 Wersja Polska

### O Projekcie

**CorrosionLab** to inżynierska aplikacja webowa (Data Science) stworzona w celu automatyzacji analizy kinetyki korozji wysokotemperaturowej. Służy do oceny skuteczności ochronnej nanokompozytowych powłok ceramicznych zol-żel (modyfikowanych m.in. ZrO2, Y2O3, CeO2, SiO2, Al2O3) nakładanych na stop oporowy FeCrAl.

Aplikacja powstała w 2026 roku jako cyfrowe rozwinięcie i ulepszenie analityczne pracy magisterskiej obronionej w 2015 roku na Wydziale Chemicznym Politechniki Wrocławskiej. Zastępuje ręczne przeliczanie wyników w arkuszach kalkulacyjnych zautomatyzowanym środowiskiem z pogranicza inżynierii materiałowej i informatyki (Materials Informatics).

### Główne Funkcjonalności

1. 📈 **Kalkulator Kinetyki:** Automatycznie wylicza względną zmianę masy ($\Delta m/m_0$), grubość zgorzeliny ($h$) oraz stałą paraboliczną szybkości utleniania ($k_p$) z prawa Tammanna.
2. ⚠️ **Detektor Odprysków:** Algorytm badający pochodną krzywej zmiany masy. Wykrywa nagłe spadki masy, flagując cykle, w których doszło do pękania i odpryskiwania zgorzeliny tlenkowej.
3. 📉 **Symulator i Ekstrapolacja:** Wykorzystuje regresję nieliniową do dopasowania funkcji (liniowej/parabolicznej) do danych empirycznych i symuluje zachowanie próbek w przyszłości (wykresy predykcyjne).
4. 🧠 **System Ekspercki:** „Doradca” powłokowy bazujący na regułach IF-THEN. Na podstawie wbudowanej wiedzy empirycznej rekomenduje optymalny napełniacz (np. tlenek cyrkonu) i liczbę warstw dla konkretnych zastosowań.

### Język interfejsu

Aplikacja obsługuje **polski** i **angielski**:

* Przy pierwszym uruchomieniu język jest wykrywany z ustawień przeglądarki (`st.context.locale`).
* Przełącznik **Język** na górze panelu bocznego pozwala wybrać Polski lub English na czas bieżącej sesji.
* Tłumaczenia znajdują się w `corrosionlab/locales/` (`pl.json`, `en.json`).

Wymagany jest **Streamlit ≥ 1.37**.

### Technologie

* **Język:** Python
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Przetwarzanie Danych:** Pandas, NumPy
* **Obliczenia Naukowe:** SciPy (`scipy.optimize.curve_fit`)
* **Wizualizacja:** Plotly

### Podgląd aplikacji

Aplikację można przetestować bez lokalnej instalacji. Wersja demonstracyjna jest dostępna na Streamlit Community Cloud:

**[https://corrosion-lab.streamlit.app](https://corrosion-lab.streamlit.app)**

### Instalacja i Uruchomienie

1. Sklonuj repozytorium:

   ```bash
   git clone https://github.com/TwojUsername/CorrosionLab.git
   cd CorrosionLab
   ```

2. Utwórz środowisko wirtualne i zainstaluj biblioteki:

   ```bash
   python -m venv venv
   source venv/bin/activate  # W systemie Windows użyj: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Uruchom aplikację Streamlit:

   ```bash
   streamlit run app.py
   ```

### Struktura Danych

Aplikacja obsługuje pliki `.csv` ze strukturą wagową dla cykli utleniania. Kolumna `TM_Control` (lub inna oznaczona jako referencja) jest niezbędna do liczenia skuteczności ochronnej powłok ($S_k$).

| time_h | TM_Control | TM1A | TM1B | TM4B |
|--------|------------|------|------|------|
| 0 | 0.01466 | 0.01500 | 0.01475 | 0.01212 |
| 12 | 0.01474 | 0.01514 | 0.01479 | 0.01204 |

### Licencja i Cytowanie

Ten projekt posiada podwójne licencjonowanie (Dual-License):

* **Oprogramowanie / Kod:** Udostępniane na licencji MIT License.
* **Treść pracy i dane badawcze:** Oryginalny plik PDF z pracą magisterską oraz zestaw danych empirycznych udostępniane są na licencji Creative Commons Attribution 4.0 International (CC BY 4.0).

**Cytowanie pracy:**

Miller, T. (2015). *Nanokompozytowe powłoki ceramiczne otrzymywane metodą zol-żel*. Praca magisterska. Wydział Chemiczny, Politechnika Wrocławska.
