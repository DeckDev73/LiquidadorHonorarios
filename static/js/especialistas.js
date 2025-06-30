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

      // Set the single specialty as the selected one
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

    const url = `/tabla_especialista?profesional=${encodeURIComponent(profesional)}&especialidad=${encodeURIComponent(especialidad)}`;
    fetch(url)
      .then(response => response.text())
      .then(html => {
        document.getElementById('tabla-especialista').innerHTML = html;
      })
      .catch(error => console.error('Error al cargar la tabla:', error));
  }

  selectEspecialista.addEventListener('change', () => {
    actualizarEspecialidades();
    setTimeout(cargarTabla, 50); // ⏳ Da tiempo a que se actualice el select
  });

  selectEspecialidad.addEventListener('change', cargarTabla);

  actualizarEspecialidades();
  cargarTabla();
});
