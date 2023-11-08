
console.log('project.js loaded')
function hello() {
    return 'world'
}
document.addEventListener('DOMContentLoaded', function() {
    console.log('dom loaded')
    hello();
    const newKVButton = document.getElementById('new-kv-submit');
    newKVButton.addEventListener('click', function() {
        console.log('hello')
        const infoElem = document.getElementById('form-info');
        infoElem.innerHTML = ''
        const k = document.getElementById('input-key').value;
        const v = document.getElementById('input-value').value;
        if (!k || !v) {
            infoElem.innerHTML = '原文译文不能为空'
        }
        console.log(k, v)

        const base_url = document.getElementById('secret-base-url-block').innerHTML;
        const user = document.getElementById('secret-user-block').innerHTML;
        const game = document.getElementById('secret-game-block').innerHTML;
        const token = document.getElementById('secret-token-block').innerHTML;


        let url = `${base_url}/api/insert/${game}/${k}/${v}`;
        url = encodeURI(url);

        const headers = new Headers({
            'Authorization': 'Basic ' + btoa(user + ':' + token)
        });

        fetch(url, {
            method: 'GET',
            headers: headers
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return true;
        })
        .catch(error => {
            infoElem.innerHTML = `${error}`
        });
        
        
        infoElem.innerHTML = '';
    })
});