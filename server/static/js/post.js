const MINUTE = 60000
const HOUR = MINUTE * 60
const DAY = HOUR * 24
const MONTH = DAY * 30
const YEAR = DAY * 365

window.onload = function() {
  vars.date_ms = vars.date * 1000
  let delay = 30

  setInterval(function() {
    update_date()
  }, 1000 * delay)

  update_date()

  let edit = DOM.el(`#edit`)
  let edit_dialog = DOM.el(`#edit_dialog`)

  if (edit && edit_dialog) {
    edit_dialog.addEventListener(`close`, () => {
      let value = edit_dialog.returnValue

      if (value === `delete`) {
        if (confirm(`Delete this post?`)) {
          delete_post()
        }
      }
      else if (value === `title`) {
        edit_title()
      }
    })

    DOM.ev(edit, `click`, () => {
      edit_dialog.showModal()
    })
  }

  if ((vars.mtype === `text/markdown`) && vars.sample) {
    let html = marked.parse(
      vars.sample.replace(/[\u200B-\u200F\uFEFF]/g, ``),
    )

    DOM.el(`#markdown_view`).innerHTML = html
  }
  else if (vars.mtype.startsWith(`application`) && vars.mtype.includes(`flash`)) {
    start_flash(vars.name)
  }

  let image = DOM.el(`#image`)

  if (image) {
    DOM.ev(image, `click`, () => {
      let modal_image = DOM.el(`#modal_image`)
      modal_image.src = image.src
      let modal = DOM.el(`#modal`)
      modal.style.display = `flex`
    })
  }

  let modal = DOM.el(`#modal`)

  if (modal) {
    DOM.ev(modal, `click`, () => {
      modal.style.display = `none`
    })
  }

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      window.location = `/`
    }
  })
}

function timeago(date) {
  let level = 0
  let diff = Date.now() - date
  let places = 1
  let result

  if (diff < MINUTE) {
    result = `just now`
    level = 1
  }
  else if (diff < HOUR) {
    let n = parseFloat((diff / MINUTE).toFixed(places))

    if (n === 1) {
      result = `${n} min ago`
    }
    else {
      result = `${n} mins ago`
    }

    level = 2
  }
  else if ((diff >= HOUR) && (diff < DAY)) {
    let n = parseFloat(diff / HOUR).toFixed(places)

    if (n === 1) {
      result = `${n} hr ago`
    }
    else {
      result = `${n} hrs ago`
    }

    level = 3
  }
  else if ((diff >= DAY) && (diff < MONTH)) {
    let n = parseFloat(diff / DAY).toFixed(places)

    if (n === 1) {
      result = `${n} day ago`
    }
    else {
      result = `${n} days ago`
    }

    level = 4
  }
  else if ((diff >= MONTH) && (diff < YEAR)) {
    let n = parseFloat(diff / MONTH).toFixed(places)

    if (n === 1) {
      result = `${n} month ago`
    }
    else {
      result = `${n} months ago`
    }

    level = 5
  }
  else if (diff >= YEAR) {
    let n = parseFloat(diff / YEAR).toFixed(places)

    if (n === 1) {
      result = `${n} year ago`
    }
    else {
      result = `${n} years ago`
    }

    level = 6
  }

  return [result, level]
}

async function edit_title() {
  let title = prompt(`New Title`, vars.title || vars.original).trim()

  if (title === vars.title) {
    return
  }

  let name = vars.name

  let response = await fetch(`/edit_title`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name, title}),
  })

  if (response.ok) {
    vars.title = title
    DOM.el(`#title`).textContent = title || vars.original
  }
  else {
    print_error(response.status)
  }
}

async function delete_post() {
  let response = await fetch(`/delete_post`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name: vars.name}),
  })

  if (response.ok) {
    DOM.el(`#title`).textContent = `DELETED 👻`
  }
  else {
    print_error(response.status)
  }
}

function print_error(msg) {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
}

function update_date() {
  let [str, level] = timeago(vars.date_ms)

  if (level > 1) {
    DOM.el(`#ago`).textContent = str
  }

  let date_1 = dateFormat(vars.date_ms, `d mmmm yyyy`)
  let date_2 = dateFormat(vars.date_ms, `hh:MM TT`)
  DOM.el(`#date_1`).textContent = date_1
  DOM.el(`#date_2`).textContent = date_2
}

function start_flash(file) {
  let ruffle = window.RufflePlayer.newest()
  let player = ruffle.createPlayer()
  player.style.width = `800px`
  player.style.height = `600px`
  let container = DOM.el(`#flash`)
  container.appendChild(player)
  player.ruffle().load(`/${vars.file_path}/${file}`)
}