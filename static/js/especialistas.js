document.addEventListener('DOMContentLoaded', function () {
  const rawData = document.getElementById('data-especialistas').textContent;
  const especialistas = JSON.parse(rawData);

  const selectEspecialista = document.getElementById('especialista');
  const selectEspecialidad = document.getElementById('especialidad');
  const containerEspecialidad = document.getElementById('especialidad-container');
  const checkboxes = document.querySelectorAll('#parametros-liquidacion input[type="checkbox"]');

  function cargarFlagsDelProfesional(callback = () => {}) {
    const profesional = selectEspecialista.value?.trim();
    if (!profesional) return;

    fetch(`/get_flag?profesional=${encodeURIComponent(profesional)}`)
      .then(res => res.json())
      .then(flags => {
        const ids = ['check_anestesia_diff', 'check_socio', 'check_reconstruc', 'check_pie'];
        ids.forEach(id => {
          const cb = document.getElementById(id);
          if (cb) cb.checked = !!flags[id];
        });
        callback(); // ejecutar después de aplicar flags
      });
  }

  function actualizarEspecialidades() {
    const profesional = selectEspecialista.value;
    const especialidades = especialistas[profesional] || [];
    selectEspecialidad.innerHTML = '';

    if (especialidades.length <= 1) {
      containerEspecialidad.style.display = 'none';
      if (especialidades.length === 1) {
        const opt = document.createElement('option');
        opt.value = especialidades[0];
        opt.textContent = especialidades[0];
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

  function cargarTablaEspecialista() {
    const profesional = selectEspecialista.value;
    const especialidad = selectEspecialidad.value || '';
    const params = new URLSearchParams({ profesional, especialidad });

    fetch(`/tabla_especialista?${params.toString()}`)
      .then(res => res.text())
      .then(html => {
        document.getElementById('tabla-especialista').innerHTML = html;
        cargarTotalLiquidado();
      });
  }

  function cargarTotalLiquidado() {
    const profesional = selectEspecialista.value;
    const especialidad = selectEspecialidad.value || '';
    const params = new URLSearchParams({ profesional, especialidad });

    fetch(`/total_liquidado?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        const el = document.getElementById("total-liquidado-box");
        if (el) {
          if (data.total_liquidado !== undefined) {
            const valorFormateado = new Intl.NumberFormat('es-CO').format(data.total_liquidado);
            el.innerHTML = `💰 Total liquidado: $${valorFormateado}`;
          } else {
            el.innerHTML = '';
          }
        }
      });
  }

  // ✅ Sin botón
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener('change', () => {
      const profesional = selectEspecialista.value;

      if (checkbox.checked) {
        checkboxes.forEach(other => {
          if (other !== checkbox) other.checked = false;
        });

        const formData = new FormData();
        formData.append('profesional', profesional);
        formData.append(checkbox.id, '1');

        fetch('/guardar_flags_liquidacion', {
          method: 'POST',
          body: formData
        }).then(() => {
          cargarFlagsDelProfesional(cargarTablaEspecialista);
        });

      } else {
        const algunoActivo = Array.from(checkboxes).some(cb => cb.checked);
        if (!algunoActivo) {
          const formData = new FormData();
          formData.append('profesional', profesional);
          fetch('/guardar_flags_liquidacion', {
            method: 'POST',
            body: formData
          }).then(() => {
            cargarFlagsDelProfesional(cargarTablaEspecialista);
          });
        }
      }
    });
  });

  // ✅ Eventos de cambio
  selectEspecialista.addEventListener('change', () => {
    actualizarEspecialidades();
    cargarFlagsDelProfesional(cargarTablaEspecialista);
  });

  selectEspecialidad.addEventListener('change', cargarTablaEspecialista);

  // ✅ Inicializar todo
  actualizarEspecialidades();
  cargarFlagsDelProfesional(() => {
    setTimeout(cargarTablaEspecialista, 50);
  });
});
