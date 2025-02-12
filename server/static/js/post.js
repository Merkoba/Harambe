const MINUTE = 60000
const HOUR = MINUTE * 60
const DAY = HOUR * 24
const MONTH = DAY * 30
const YEAR = DAY * 365

window.onload = function() {
  let ago = document.querySelector(`#ago`)
  vars.date_ms = vars.date * 1000

  if (ago) {
    let delay = 30

    setInterval(function() {
      let [str, level] = timeago(vars.date_ms)

      if (level > 1) {
        ago.innerHTML = str
      }
    }, 1000 * delay)
  }

  let edit = document.querySelector(`#edit`)

  if (edit) {
    edit.addEventListener(`click`, () => {
      edit_title()
    })
  }

  let del = document.querySelector(`#delete`)

  if (del) {
    del.addEventListener(`click`, () => {
      if (confirm(`Delete this file?`)) {
        delete_file()
      }
    })
  }
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
  let title = prompt(`New Title`, vars.title).trim()

  if (!title) {
    return
  }

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
    document.querySelector(`#title`).textContent = title
  }
  else {
    print_error(response.status)
  }
}

async function delete_file() {
  let response = await fetch(`/delete_file`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name: vars.name, file: vars.full}),
  })

  if (response.ok) {
    document.querySelector(`#title`).textContent = `DELETED 👻`
  }
  else {
    print_error(response.status)
  }
}

function print_error(msg) {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
}