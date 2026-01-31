document.getElementById('formApresentacao').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btnGerar = document.getElementById('btnGerar');
    const loading = document.getElementById('loading');
    const resultado = document.getElementById('resultado');
    
    // Mostrar loading
    btnGerar.disabled = true;
    loading.style.display = 'block';
    resultado.style.display = 'none';
    
    try {
        const formData = new FormData(this);
        
        const response = await fetch('/gerar', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ erro: 'Erro no servidor' }));
            throw { message: errorData.erro || 'Erro na requisição', detalhes: errorData.detalhes };
        }
        
        const data = await response.json();
        
        loading.style.display = 'none';
        resultado.style.display = 'block';
        
        if (data.sucesso) {
            resultado.className = 'resultado sucesso';
            resultado.innerHTML = `
                <h3>✅ Apresentação gerada com sucesso!</h3>
                <p>Seu arquivo está pronto para download.</p>
                <a href="/download/${data.arquivo}" class="btn-download">
                    ⬇️ Baixar Apresentação (HTML)
                </a>
            `;
        } else {
            // Propagar o erro com detalhes
            const error = new Error(data.erro || 'Erro desconhecido');
            error.detalhes = data.detalhes;
            throw error;
        }
        
    } catch (error) {
        loading.style.display = 'none';
        resultado.style.display = 'block';
        resultado.className = 'resultado erro';
        
        let errorHTML = `
            <h3>❌ Erro ao gerar apresentação</h3>
            <p>${error.message}</p>
        `;
        
        // Se houver detalhes técnicos na resposta
        if (error.detalhes) {
            errorHTML += `
                <details style="margin-top: 15px; text-align: left; background: white; padding: 15px; border-radius: 6px;">
                    <summary style="cursor: pointer; font-weight: bold;">Ver detalhes técnicos</summary>
                    <pre style="margin-top: 10px; overflow-x: auto; font-size: 0.85em;">${error.detalhes}</pre>
                </details>
            `;
        }
        
        resultado.innerHTML = errorHTML;
    } finally {
        btnGerar.disabled = false;
    }
});

// Preview de imagens
document.getElementById('imagens').addEventListener('change', function(e) {
    const preview = document.getElementById('preview-imagens');
    preview.innerHTML = '';
    
    if (this.files.length > 0) {
        preview.innerHTML = '<strong>Imagens selecionadas:</strong><br>';
        Array.from(this.files).forEach(file => {
            const item = document.createElement('div');
            item.className = 'preview-item';
            item.innerHTML = `📎 ${file.name} <br><code>![](Figuras/${file.name})</code>`;
            preview.appendChild(item);
        });
    }
});
