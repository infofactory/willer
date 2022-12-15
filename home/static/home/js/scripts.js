function reloadMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: {lat:45, lng:12},
        zoom: 6,
    })
    navigator.geolocation.getCurrentPosition(function(pos) {
        const user_position = {lat: pos.coords.latitude, lng:pos.coords.longitude}
        new google.maps.Marker({
            position: user_position,
            map,
        })
        map.setZoom(14)
        map.setCenter(user_position)

        fetch('/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: `lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`
        })

        document.querySelector('.slide[data-page="1"] .btn.next').style.display = ''
        document.querySelector('.slide[data-page="1"] .alert-danger').style.display = 'none'

    })
}


const buttons = document.querySelectorAll('.pagination a.btn')
const slideshow = document.getElementById('slideshow')

document.addEventListener('DOMContentLoaded', function() {
    if (slideshow.dataset.page == 1) {
        reloadMap()
    }
})

for (const button of buttons) {
    button.addEventListener('click', function(e) {
        if (this.getAttribute('href').length > 1) {
            return
        }
        if (this.classList.contains('prev')) {
            slideshow.dataset.page--
        } else if (this.classList.contains('next')) {
            if (this.dataset.page) {
                slideshow.dataset.page = this.dataset.page
            } else {
                slideshow.dataset.page++
            }
        }
        slideshow.style.transform = 'translateX(-' + slideshow.dataset.page * 100 + 'vw)'
        window.scrollTo(0, 0)
        if (slideshow.dataset.page == 1) {
            reloadMap()
        }

        const slideHeight = document.querySelector('.slide[data-page="' + slideshow.dataset.page + '"]').clientHeight 
        slideshow.style.height = slideHeight + 90 + 'px'
        e.preventDefault()
    })
}



const toggles = document.querySelectorAll('.choices.devices .choice.square label')
for (const toggle of toggles) {
    toggle.addEventListener('click', function() {
        this.classList.toggle('selected')

        const radio_group = this.closest('.choice').nextElementSibling
        if (radio_group.classList.contains('radio-group')) {
            radio_group.style.visibility = this.classList.contains('selected') ? 'visible' : 'hidden'

            const device_name = radio_group.querySelector('input').name
            const picture_form = document.querySelector('.choices[rel=' + device_name + ']')
            picture_form.style.display = this.classList.contains('selected') ? 'flex' : 'none'

            const change = new Event('change');
            radio_group.querySelector('input:checked').dispatchEvent(change)
        }

        document.querySelector('.slide[data-page="4"] .btn.next').style.display = document.querySelectorAll('.choices.devices .choice.square label.selected').length ? 'inline' : 'none'
        document.querySelector('.slide[data-page="5"] .btn.next').style.display = checkValidFiles() ? '' : 'none'

    })
}


const inputs = document.querySelectorAll('input[type=radio], input[type=checkbox], input[type=text], select')
for (const input of inputs) {
    input.addEventListener('change', function() {

        if (this.name == 'levels') {
            document.getElementById('step-free').style.visibility = this.value == '1' ? 'visible' : 'hidden'
            const nextButton = this.closest('.slide').querySelector('.btn.next')
            nextButton.dataset.page = this.value == '1' ? 7 : 4
        }
        fetch('/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: this.name + '=' + encodeURIComponent(this.value)
        })
    })
}


function somethingWorking() {
    // Controllo se ne funziona almeno uno per mostrare il messaggio
    const reportChoices = document.querySelectorAll('.choices[rel]')
    let some_is_working = false
    for (const reportChoice of reportChoices) {
        // Se si vede e ha il testo "working"
        if (window.getComputedStyle(reportChoice, null).display != 'none' &&
            reportChoice.querySelector('p').textContent.includes('working')) {
                some_is_working = true
        }
    }
    document.getElementById('nothing-working').style.display = some_is_working ? 'none' : 'block'
}

function showPictureForm() {
    const selectedText = this.closest('label').textContent
    const picture_form = document.querySelector('.choices[rel=' + this.name + ']')
    picture_form.querySelector('p').textContent = selectedText
    somethingWorking()
}



const radios = document.querySelectorAll('.radio-group input')
for (const radio of radios) {
    radio.addEventListener('change', showPictureForm)
}



const fileInputs = document.querySelectorAll('input[type=file]')

// Controlla se tutte le foto sono state caricate, controllo solo gli input visibili
function checkValidFiles() {
    let allFilesSelected = true
    for (const fileInput of fileInputs) {
        const choices = fileInput.closest('.choices')
        if (window.getComputedStyle(choices).display != 'none') {
            const [file] = fileInput.files
            if (!file) {
                allFilesSelected = false
            }
        }
    }
    return allFilesSelected
}


for (const fileInput of fileInputs) {
    fileInput.addEventListener('change', function() {
        const [file] = this.files
        if (file) {
            this.previousElementSibling.src = URL.createObjectURL(file)

            const data = new FormData()
            data.append(this.name, file)
            fetch('/save/', {
                method: 'POST',
                body: data
            })
        }

        document.querySelector('.slide[data-page="5"] .btn.next').style.display = checkValidFiles() ? '' : 'none'

    })
}

/*
 + VALIDAZIONI
 */
// Train or metro
for (elem of document.querySelectorAll('input[name=station]')) {
    elem.addEventListener('change', () => {
        document.querySelector('.slide[data-page="2"] .btn.next').style.display = document.querySelectorAll('input[name=station]:checked').length ? '' : 'none'
    })
}

// Levels
for (elem of document.querySelectorAll('input[name=levels], input[name=step_free]')) {
    elem.addEventListener('change', () => {
        document.querySelector('.slide[data-page="3"] .btn.next').style.display = document.querySelectorAll('input[name=levels][value="2"]:checked, input[name=step_free]:checked').length ? '' : 'none'
    })
}

