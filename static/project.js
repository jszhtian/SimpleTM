
console.log('project.js loaded')
const pastedTableRegex = /([^\t]+\t[^\t]+)(\n[^\t]+\t[^\t]+)*/;
document.addEventListener('DOMContentLoaded', async function() {
    console.log('dom loaded')
    const base_url = document.getElementById('secret-base-url-block').innerHTML;
    const user = document.getElementById('secret-user-block').innerHTML;
    const game = document.getElementById('secret-game-block').innerHTML;
    const token = document.getElementById('secret-token-block').innerHTML;
    const infoElem = document.getElementById('info-div');

    const inputKeyElem = document.getElementById('input-key');
    inputKeyElem.addEventListener('paste', async function(event) {
        var clipboardData = event.clipboardData || window.clipboardData;
        var pastedText = clipboardData.getData('text');
        console.log(pastedText);
        if (pastedTableRegex.test(pastedText)) {
            event.preventDefault();
            const kvs = pastedText.split('\n').map(kv => kv.split('\t').map(s=>s.trim()));
            
            for (const [k, v] of kvs) {
                const skip = false;
                for (const { raw, translate } of dict) {
                    if (k === raw) {
                        skip = true;
                        break;
                    }
                }
                if (skip) {
                    continue;
                }
                const r = await makeRequest(encodeURI(`${base_url}/api/insert/${game}/${k}/${v}`));
                if (r && r.Result == "True") {
                    addRow(k, v);
                    dict.push({ "raw": k, "translate": v });
                }
            }
            
        }
    });


    function makeRequest(url) {
        const headers = new Headers({
            'Authorization': 'Basic ' + btoa(user + ':' + token)
        });

        infoElem.innerHTML = '';

        return fetch(url, {
            method: 'GET',
            headers: headers
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .catch(error => {
            infoElem.innerHTML = `${error}`
        });
    }

    async function addRow(raw, translate) {
        const row = document.createElement('tr');
        const ktd = document.createElement('td');
        const kelem = document.createElement('input');
        ktd.appendChild(kelem);
        kelem.disabled = true;
        kelem.value = raw;
        row.k_value = raw;

        const vtd = document.createElement('td');
        const velem = document.createElement('input');
        vtd.appendChild(velem);
        velem.value = translate;
        velem.k_value = kelem.value;
        row.appendChild(ktd);
        row.appendChild(vtd);
        tb.appendChild(row);

        const delBtn = document.createElement('button');
        delBtn.k_value = kelem.value;
        delBtn.innerText = '删除';
        delBtn.addEventListener("click", async function() {
            const k = this.k_value;
            const r = await makeRequest(encodeURI(`${base_url}/api/delete/${game}/${k}`));
            if (r && r.Result == "True") {
                const tb = document.getElementById('content-table-body');
                for (let i = 0; i < tb.children.length; i++) {
                    const row = tb.children[i];
                    if (row.k_value == k) {
                        row.remove();
                    }
                }
                for(let i = 0; i < dict.length; i++) {
                    if (k == dict[i].raw) {
                        dict.splice(i, 1);
                        break;
                    }
                }
            }
        })
        row.appendChild(delBtn);

        velem.addEventListener("blur", async function() {
            const k = this.k_value;
            const v = this.value;
            if (!v) {
                infoElem.innerHTML = '译文不能为空';
                return;
            }
            await makeRequest(encodeURI(`${base_url}/api/update/${game}/${k}/${v}`));
        });
    }
    
    const tb = document.getElementById('content-table-body');
    const dict = await makeRequest(encodeURI(`${base_url}/api/querybygame/${game}`));
    console.log(dict)

    for(const {raw, translate} of dict) {
        addRow(raw, translate);
    }

    const newKVButton = document.getElementById('new-kv-submit');
    newKVButton.addEventListener('click', async function() {
        infoElem.innerHTML = ''
        const k = document.getElementById('input-key').value;
        const v = document.getElementById('input-value').value;
        if (!k || !v) {
            infoElem.innerHTML = '原文译文不能为空'
        }
        console.log(k, v)
        for(const {raw, translate} of dict) {
            if (k == raw) {
                infoElem.innerHTML = '原文不能重复';
                return;
            }
        }
        const r = await makeRequest(encodeURI(`${base_url}/api/insert/${game}/${k}/${v}`));
        if (r && r.Result == "True") {
            addRow(k, v);
            dict.push({"raw": k, "translate": v});
        }
    })

});

