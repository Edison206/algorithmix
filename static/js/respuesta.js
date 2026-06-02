function respuesta_funcion() {
    let valor = document.getElementById('valor_html').value;
    let id    = document.getElementById('id_html').value;

    fetch('../../agregar_respuesta/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `valor=${valor}&id=${id}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // ===== MOSTRAR RETROALIMENTACIÓN =====
            const caja          = document.getElementById('retroalimentacion');
            const icono         = document.getElementById('retro_icono');
            const titulo        = document.getElementById('retro_titulo');
            const mensaje       = document.getElementById('retro_mensaje');
            const valorMostrado = document.getElementById('retro_valor');
            const recomBox      = document.getElementById('retro_recomendacion_box');
            const recomTexto    = document.getElementById('retro_recomendacion');

            mensaje.textContent       = data.mensaje;
            valorMostrado.textContent = valor;

            if (data.correcto) {
                caja.className     = 'retro_caja correcto';
                icono.textContent  = '✓';
                titulo.textContent = 'Correcto';
            } else {
                caja.className     = 'retro_caja incorrecto';
                icono.textContent  = '✗';
                titulo.textContent = 'Incorrecto';
            }

            if (data.recomendacion) {
                recomTexto.textContent = data.recomendacion;
                recomBox.style.display = 'block';
            } else {
                recomBox.style.display = 'none';
            }

            caja.style.display = 'block';

            // ===== ACTUALIZAR CONTADOR DE INTENTOS =====
            const contadorEl = document.getElementById('contador_intentos');
            const nuevoTotal = parseInt(contadorEl.textContent) + 1;
            contadorEl.textContent = nuevoTotal;

            // ===== AGREGAR EL NUEVO INTENTO AL HISTORIAL =====
            const listaIntentos = document.getElementById('lista_intentos');
            const claseDot      = data.correcto ? 'bien' : 'mal';
            const fechaActual   = new Date().toLocaleString('es-EC');

            const nuevoIntentoHTML = `
                <div class="attempt">
                    <div class="dot ${claseDot}"></div>
                    <div class="attempt-info">
                        <span>Intento: ${nuevoTotal}</span>
                        <span>${valor}</span>
                        <small>${fechaActual}</small>
                    </div>
                </div>
            `;
            listaIntentos.insertAdjacentHTML('beforeend', nuevoIntentoHTML);

            // ===== LIMPIAR EL CAMPO DE RESPUESTA =====
            document.getElementById('valor_html').value = '';

            // ===== SI LLEGÓ AL LÍMITE DE 3, OCULTAR EL FORMULARIO =====
            if (nuevoTotal >= 3) {
                document.querySelector('.fake-input').style.display = 'none';
                document.querySelector('.btn').style.display = 'none';
                document.querySelector('.answer-section h3').style.display = 'none';

                // Mostrar mensaje de límite alcanzado
                const answerSection = document.querySelector('.answer-section');
                const mensajeLimite = `
                    <div class="limit-message1">
                        <div class="limit-message2">
                            <h3>Has alcanzado el límite de intentos</h3>
                        </div>
                    </div>
                `;
                answerSection.insertAdjacentHTML('beforeend', mensajeLimite);
            }
        }
    });
}