import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import ElementClickInterceptedException
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

@pytest.fixture(params=["chrome", "firefox", "edge"], scope="module")
def driver(request):
    logger.info(f"Iniciando el navegador: {request.param}")
    if request.param == "chrome":
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--start-fullscreen")
        driver = webdriver.Chrome(options=chrome_options)
    elif request.param == "firefox":
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--kiosk")
        driver = webdriver.Firefox(options=firefox_options)
        driver.maximize_window()
    elif request.param == "edge":
        edge_options = EdgeOptions()
        edge_options.add_argument("--start-fullscreen")
        driver = webdriver.Edge(options=edge_options)
    else:
        raise ValueError(f"Navegador no soportado: {request.param}")
    driver.get('http://localhost:8050')
    yield driver
    driver.quit()
    logger.info(f"Navegador cerrado: {request.param}")

def test_filtros_presentes(driver):
    logger.info("Iniciando validación de existencia de los filtros")
    wait = WebDriverWait(driver, 60)
    anno_filtro = wait.until(EC.presence_of_element_located((By.ID, 'anno-filtro')))
    assert anno_filtro.is_displayed()
    trimestre_filtro = wait.until(EC.presence_of_element_located((By.ID, 'trimestre-filtro')))
    assert trimestre_filtro.is_displayed()
    departamento_filtro = wait.until(EC.presence_of_element_located((By.ID, 'departamento-filtro')))
    assert departamento_filtro.is_displayed()
    municipio_filtro = wait.until(EC.presence_of_element_located((By.ID, 'municipio-filtro')))
    assert municipio_filtro.is_displayed()
    logger.info("Filtros existentes")

def test_titulos_dinamicos(driver):
    logger.info("Iniciando validación de títulos dinámicos")
    wait = WebDriverWait(driver, 60)
    encabezado = wait.until(EC.presence_of_element_located((By.ID, 'encabezado')))
    assert encabezado.is_displayed()
    titulo = wait.until(EC.presence_of_element_located((By.ID, 'titulo')))
    assert titulo.is_displayed()
    logger.info("Títulos existentes")

def test_filtros_funcionales(driver):
    logger.info("Iniciando validación de funcionamiento de filtros")
    wait = WebDriverWait(driver, 30)
    time.sleep(30)
    anno_filtro = wait.until(EC.element_to_be_clickable((By.ID, 'anno-filtro')))
    anno_filtro.click()
    anno_opciones = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='anno-filtro']//div[contains(@class, 'VirtualizedSelectOption')]")))
    for opcion in anno_opciones:
        if opcion.text == '2022':
            opcion.click()
            break
    logger.info("Filtro año funcional")
    time.sleep(2)
    trimestre_filtro = wait.until(EC.element_to_be_clickable((By.ID, 'trimestre-filtro')))
    driver.execute_script("arguments[0].scrollIntoView(true);", trimestre_filtro)
    time.sleep(1)
    trimestre_filtro.click()
    trimestre_opciones = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='trimestre-filtro']//div[contains(@class, 'VirtualizedSelectOption')]")))
    for opcion in trimestre_opciones:
        if opcion.text == '2':
            opcion.click()
            break
    logger.info("Filtro trimestre funcional")
    time.sleep(2)
    departamento_filtro = wait.until(EC.element_to_be_clickable((By.ID, 'departamento-filtro')))
    driver.execute_script("arguments[0].scrollIntoView(true);", departamento_filtro)
    time.sleep(1)
    departamento_filtro.click()
    departamento_opciones = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='departamento-filtro']//div[contains(@class, 'VirtualizedSelectOption')]")))
    for opcion in departamento_opciones:
        if opcion.text == 'CUNDINAMARCA':
            opcion.click()
            break
    logger.info("Filtro departamento funcional")
    time.sleep(2)
    municipio_filtro = wait.until(EC.element_to_be_clickable((By.ID, 'municipio-filtro')))
    driver.execute_script("arguments[0].scrollIntoView(true);", municipio_filtro)
    time.sleep(1)
    municipio_filtro.click()
    municipio_opciones = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='municipio-filtro']//div[contains(@class, 'VirtualizedSelectOption')]")))
    for opcion in municipio_opciones:
        if opcion.text == 'APULO':
            opcion.click()
            break
    logger.info("Filtro municipio funcional")
    time.sleep(2)

@pytest.mark.parametrize("tab_index, tab_nombre, graph_ids", [
    (1, 'Portada', ['tab6-graph1']),
    (2, 'Mercado', ['tab1-graph1', 'tab1-graph2', 'tab1-graph3', 'tab1-graph4']),
    (3, 'Ingresos', ['tab2-graph1', 'tab2-graph2', 'tab2-graph3', 'tab2-graph4']),
    (4, 'Velocidad de Descarga', ['tab3-graph1', 'tab3-graph2']),
    (5, 'Tecnología de Conexión', ['tab4-graph1']),
    (6, 'Quejas', ['tab5-graph1', 'tab5-graph2', 'tab5-graph3', 'tab5-graph4'])
])

def test_verificar_tabs(driver, tab_nombre, tab_index, graph_ids):
    logger.info("Iniciando validación de pestañas y gráficos")
    tab_xpath = f"//*[@id='tabs']/div[{tab_index}]"
    tab = WebDriverWait(driver, 180).until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))
    tab.click()
    wait = WebDriverWait(driver, 180)
    wait.until(EC.visibility_of_element_located((By.ID, graph_ids[0])))
    for graph_id in graph_ids:
        graph = driver.find_element(By.ID, graph_id)
        assert graph.is_displayed(), f"{graph_id} no se muestra correctamente en la pestaña {tab_nombre}"
        logger.info(f"Pestaña {tab_nombre} gráfico {graph_id} funcionales")
    
def test_indicadores(driver):
    logger.info("Iniciando validación de indicadores")
    wait = WebDriverWait(driver, 30)
    total_accesos_gauge = wait.until(EC.presence_of_element_located((By.ID, 'total-accesos-gauge')))
    assert total_accesos_gauge.is_displayed()
    velocidad_promedio_gauge = wait.until(EC.presence_of_element_located((By.ID, 'velocidad-promedio-gauge')))
    assert velocidad_promedio_gauge.is_displayed()
    ingresos_gauge = wait.until(EC.presence_of_element_located((By.ID, 'ingresos-gauge')))
    assert ingresos_gauge.is_displayed()
    quejas_gauge = wait.until(EC.presence_of_element_located((By.ID, 'quejas_gauge')))
    assert quejas_gauge.is_displayed()
    logger.info("Indicadores existentes")

