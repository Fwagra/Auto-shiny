

const app = {
    suffixes: ['', '-a', '-g'],
    pokemonList : [],
    init: function(){
        app.getDataList();
        app.getUsbList();
        
        const image = document.querySelector('#pokemon_img');
        if(image.value != "") {
            app.updateImage(image.value);
        } 

        document.querySelector('#pokemon_choice').addEventListener('keyup', app.searchInList);
        document.querySelector('#pokemon_choice').addEventListener('click', app.emptySearch);
        document.querySelector('#search button').addEventListener('click', app.searchPokemon);
        document.querySelector('#release button').addEventListener('click', app.releasePokemon);
        document.querySelector('#boxes').addEventListener('keyup', app.updateReleasedPokemon);
        for(let stopBtn of document.querySelectorAll('.stop')){
            stopBtn.addEventListener('click', app.stopCommand);
        }
        for(let link of document.querySelectorAll('nav li')) {
            link.addEventListener('click', app.handleNav);
        }
    },
    handleNav: function(event) {
        let page = event.currentTarget.dataset.element;
        for(let element of document.querySelectorAll('.element')) {
            element.classList.remove('active');
        }
        document.querySelector('.'+page).classList.add('active');
        for(let link of document.querySelectorAll('nav li')) {
            if(link.dataset.element == page) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        }

    },
    getDataList: function() {
        fetch("./pokemon.json")
        .then(response => {
           return response.json();
        })
        .then(data => app.pokemonList = data);
    },
    emptySearch: function(event) {
        event.currentTarget.value = ''; 
    },
    releasePokemon: function(event) {
        event.preventDefault();

        let form = document.querySelector('#release');

        form.querySelector('button').disabled = true;
        let formData = new FormData(form);

        let options = {
            method: "POST",
            body: formData,
        };

        fetch('commands.php', options).then(res => res.json())
        .then(function(json){
            form.querySelector('button').disabled = false;
        });
    },
    updateReleasedPokemon: function(event){
        let boxes = event.currentTarget.value;
        document.querySelector('#release_eggs').value = parseInt(boxes) * 30;
    },
    searchInList: function(event) {
        event.preventDefault();
        let value = event.currentTarget.value.toLowerCase();
        
        let selected = document.querySelector('.result > .selected');
        if(event.key == "ArrowDown") {
            if(selected != null) {
                if(selected.nextElementSibling != null) {
                    selected.nextElementSibling.classList.add('selected');
                    selected.classList.remove('selected');
                }
            } else {
                document.querySelector('.result > div:first-of-type').classList.add('selected');
            }
        } else if(event.key == "ArrowUp") {
            if(selected != null && selected.previousElementSibling != null) {
                selected.previousElementSibling.classList.add('selected');
                selected.classList.remove('selected');
            }
        } else if (event.key == "Enter") {
            if(selected != null) {
                app.selectPokemon(selected);
            }
        }
        else if(value.length >= 3) {
            let result = app.pokemonList.filter(pokemon => pokemon.fr.toLowerCase().includes(value));
            app.populateSelect(result);
        }else {
            app.closeResults();
        }
    },
    closeResults: function() {
        let container = document.querySelector('.result'); 
        container.innerHTML = '';
        container.classList.add('hidden');
    },
    populateSelect: function(results) {
        let container = document.querySelector('.result'); 
        container.innerHTML = '';
        container.classList.remove('hidden');
        if (results.length) {            
            for (let pokemon of results) {
                let newPoke = document.createElement('div');
                newPoke.classList.add('poke-result');
                newPoke.innerHTML = pokemon.fr;
                newPoke.dataset.id = pokemon.id;
                newPoke.dataset.img = app.cleanName(pokemon.fr);
                newPoke.dataset.cycles = pokemon.cycles;
                newPoke.addEventListener('click', app.refreshData);
                container.appendChild(newPoke);
            }
        } else {
            container.innerHTML = "No results";
        }
    },
    cleanName: function(name) {
        let cleanedName = app.strNoAccent(name.toLowerCase());
        cleanedName = cleanedName.replace(' ', '');
        cleanedName = cleanedName.replace('.', '');
        cleanedName = cleanedName.replace(':', '');
        return cleanedName;
    },
    refreshData: function(event){
        let pokemon = event.currentTarget;
       app.selectPokemon(pokemon);

    },
    selectPokemon: function (pokemon) {
        app.updateCycles(pokemon.dataset.cycles);
        app.updateImage(pokemon.dataset.img);
        document.querySelector('#pokemon_choice').value = pokemon.innerHTML;
        document.querySelector('#pokemon_img').value = pokemon.dataset.img;
        app.closeResults();
    },
    updateCycles: function(cycles) {
        document.querySelector('#cycles').value = cycles;
                
    },
    updateImage: function(img) {
        let erasedSprite = false;
        const spriteContainer = document.querySelector('.sprite');
        for(let suffix of app.suffixes) {
            const url = 'img/shiny/'+img+suffix+'.png';
            if(app.imageExists(url)) {
                if(!erasedSprite) {
                    spriteContainer.innerHTML = "";
                    erasedSprite = true;
                }
                let div = document.createElement('div');
                let image = document.createElement('img');
                image.src = url;
                div.appendChild(image)
                spriteContainer.appendChild(div);
            }
        }
    },
    imageExists: function(image_url){

        var http = new XMLHttpRequest();
    
        http.open('HEAD', image_url, false);
        http.send();
    
        return http.status != 404;
    
    },
    searchPokemon: function(event) {
        event.preventDefault();

        

        let form = document.querySelector('#search');

        form.querySelector('button').disabled = true;
        let formData = new FormData(form);

        let options = {
            method: "POST",
            body: formData,
        };

        fetch('commands.php', options).then(res => res.json())
        .then(function(json){
            form.querySelector('button').disabled = false;
        });
    },
    getUsbList: function() {

        let formData = new FormData();
        formData.append('command', 'usb');


        let options = {
            method: "POST",
            body: formData,
        };
        fetch('commands.php', options).then(res => res.json())
        .then(function(json){
            let select = document.querySelectorAll('.usb');

            for(selectElement of select) {

                for(let usb of json) {
                    let option = document.createElement('option');
                    option.value = usb;
                    option.innerText = usb;
                    if(app.getCookie('usb') == usb) {
                        option.selected = true;
                    }
                    selectElement.appendChild(option);
                }
            }
            
        })
    },
    stopCommand: function() {

        let formData = new FormData();
        formData.append('command', 'stop');


        let options = {
            method: "POST",
            body: formData,
        };
        fetch('commands.php', options).then(res => res.json())
        .then(function(json){
            document.querySelector('#search button').disabled = false; 
            document.querySelector('#release button').disabled = false; 
        })
    },
    strNoAccent: function(a) {
        var b="áàâäãåçéèêëíïîìñóòôöõúùûüýÁÀÂÄÃÅÇÉÈÊËÍÏÎÌÑÓÒÔÖÕÚÙÛÜÝ",
            c="aaaaaaceeeeiiiinooooouuuuyAAAAAACEEEEIIIINOOOOOUUUUY",
            d="";
        for(var i = 0, j = a.length; i < j; i++) {
          var e = a.substr(i, 1);
          d += (b.indexOf(e) !== -1) ? c.substr(b.indexOf(e), 1) : e;
        }
        return d;
    },
    getCookie: function(name) {
        let cookie = {};
        document.cookie.split(';').forEach(function(el) {
          let [k,v] = el.split('=');
          cookie[k.trim()] = v;
        })
        return cookie[name];
      }
      
}

document.addEventListener('DOMContentLoaded', app.init);