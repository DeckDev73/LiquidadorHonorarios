document.addEventListener('DOMContentLoaded', function () {
  const rawData = document.getElementById('data-especialistas').textContent;
  const especialistas = JSON.parse(rawData);

  const selectEspecialista = document.getElementById('especialista');
  const selectEspecialidad = document.getElementById('especialidad');
  const containerEspecialidad = document.getElementById('especialidad-container');

  function actualizarEspecialidades() {
    const profesional = selectEspecialista.value;
    const especialidades = especialistas[profesional] || [];

    selectEspecialidad.innerHTML = '';

    if (especialidades.length <= 1) {
      containerEspecialidad.style.display = 'none';

      if (especialidades.length === 1) {
        const unica = especialidades[0];
        const opt = document.createElement('option');
        opt.value = unica;
        opt.textContent = unica;
        opt.selected = true;
        selectEspecialidad.appendChild(opt);
      }
    } else {
      containerEspecialidad.style.display = 'block';

      especialidades.forEach(esp => {
        const opt = document.createElement('option');
        opt.value = esp;
        opt.textContent = esp;
        selectEspecialidad.appendChild(opt);
      });
    }
  }

  function cargarTabla() {
    const profesional = selectEspecialista.value;
    const especialidad = selectEspecialidad.value || '';

    // Leer checkboxes
    const checkAnestesia = document.getElementById('check_anestesia_diff')?.checked || false;
    const checkSocio = document.getElementById('check_socio')?.checked || false;
    const checkReconstruc = document.getElementById('check_reconstruc')?.checked || false;
    const checkPie = document.getElementById('check_pie')?.checked || false;

    const params = new URLSearchParams({
      profesional,
      especialidad,
      check_anestesia_diff: checkAnestesia,
      check_socio: checkSocio,
      check_reconstruc: checkReconstruc,
      check_pie: checkPie,
    });

    fetch(`/tabla_especialista?${params.toString()}`)
      .then(response => response.text())
      .then(html => {
        document.getElementById('tabla-especialista').innerHTML = html;
      })
      .catch(error => console.error('Error al cargar la tabla:', error));
  }

  selectEspecialista.addEventListener('change', () => {
    actualizarEspecialidades();
    setTimeout(cargarTabla, 50);
  });

  selectEspecialidad.addEventListener('change', cargarTabla);

  // ⏫ Escucha eventos de los checkboxes de parámetros
  document.querySelectorAll('#parametros-liquidacion input[type=checkbox]').forEach(cb => {
    cb.addEventListener('change', cargarTabla);
  });

  actualizarEspecialidades();
  cargarTabla();
});
