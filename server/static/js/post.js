const MINUTE = 60000
const HOUR = MINUTE * 60
const DAY = HOUR * 24
const MONTH = DAY * 30
const YEAR = DAY * 365

window.onload = function() {
  vars.date_ms = vars.date * 1000
  vars.icons_loaded = false
  vars.selected_icon = ``
  vars.refresh_count = 0

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
      let modal_image = DOM.el(`#image_modal_img`)
      modal_image.src = image.src
      let modal = DOM.el(`#image_modal`)
      DOM.show(modal)
    })
  }

  let modal = DOM.el(`#image_modal`)

  if (modal) {
    DOM.ev(modal, `click`, () => {
      DOM.hide(modal)
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

  let r_icon = DOM.el(`#react_icon`)

  if (r_icon) {
    DOM.ev(r_icon, `click`, () => {
      show_icons()
    })
  }

  let r_character = DOM.el(`#react_character`)

  if (r_character) {
    DOM.ev(r_character, `click`, () => {
      react_character()
    })
  }

  let r_modal = DOM.el(`#icons_modal`)

  if (r_modal) {
    DOM.ev(r_modal, `click`, (e) => {
      if (e.target.id === `icons_modal`) {
        DOM.hide(r_modal)
      }
    })

    let r_input = DOM.el(`#icons_input`)

    if (r_input) {
      DOM.ev(r_input, `input`, () => {
        filter_icons()
      })
    }

    DOM.ev(r_input, `keydown`, (e) => {
      if (e.key === `Escape`) {
        esc_icons()
        e.preventDefault()
      }
      else if (e.key === `Enter`) {
        enter_icons()
        e.preventDefault()
      }
      else if (e.key === `ArrowUp`) {
        up_icons()
        e.preventDefault()
      }
      else if (e.key === `ArrowDown`) {
        down_icons()
        e.preventDefault()
      }
    })

    DOM.ev(r_modal, `click`, (e) => {
      if (e.target.closest(`.icon_item`)) {
        let item = e.target.closest(`.icon_item`)
        vars.selected_icon = item.dataset.icon
        enter_icons()
      }
    })
  }

  DOM.ev(document, `keyup`, (e) => {
    if (e.key === `r`) {
      if (!icons_open()) {
        show_icons()
      }
    }
  })

  vars.refresh_interval = setInterval(() => {
    refresh()
    vars.refresh_count += 1

    if (vars.refresh_count >= vars.post_refresh_times) {
      clearInterval(vars.refresh_interval)
    }
  }, vars.post_refresh_interval * 1000)

  let rev = DOM.el(`#reveal_reactions`)

  if (rev) {
    DOM.ev(rev, `click`, () => {
      reveal_reactions()
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
  let title = prompt(`New Title`, vars.title || vars.original)

  if (!title) {
    return
  }

  title = title.trim()

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
  let name = vars.name

  let response = await fetch(`/delete_post`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name}),
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

function react_alert() {
  alert(`You might have to login to react.`)
}

async function show_icons() {
  if (!vars.can_react) {
    react_alert()
    return
  }

  let modal = DOM.el(`#icons_modal`)
  let container = DOM.el(`#icons`)

  if (!vars.icons_loaded) {
    let response = await fetch(`/get_icons`)

    if (!response.ok) {
      print_error(response.status)
      return
    }

    let json = await response.json()
    container.innerHTML = ``
    let icons = shuffle_array(json.icons)

    for (let icon of icons) {
      let item = DOM.create(`div`, `icon_item`)
      let text = DOM.create(`div`, `icon_item_text`)
      text.textContent = icon
      item.appendChild(text)
      let img = DOM.create(`img`, `icon_item_img`)
      img.loading = `lazy`
      img.src = `/static/icons/${icon}.gif`
      item.appendChild(img)
      item.dataset.icon = icon
      container.appendChild(item)
    }

    vars.icons_loaded = true
  }
  else {
    show_all_icons()
  }

  DOM.show(modal)
  let input = DOM.el(`#icons_input`)
  input.value = ``
  input.focus()
  select_first_icon()
  container.scrollTop = 0
}

function filter_icons() {
  let r_input = DOM.el(`#icons_input`)
  let value = r_input.value.toLowerCase()
  let icons = DOM.el(`#icons`)
  let children = icons.children

  for (let child of children) {
    if (child.textContent.includes(value)) {
      DOM.show(child)
    }
    else {
      DOM.hide(child)
    }
  }

  select_first_icon()
}

function select_first_icon() {
  let icons = DOM.el(`#icons`)
  let children = icons.children
  let selected = false

  for (let child of children) {
    if (selected) {
      child.classList.remove(`selected`)
    }
    else if (!DOM.is_hidden(child)) {
      child.classList.add(`selected`)
      vars.selected_icon = child.textContent
      selected = true
    }
  }
}

function esc_icons() {
  let r_input = DOM.el(`#icons_input`)

  if (r_input.value) {
    r_input.value = ``
    filter_icons()
  }
  else {
    DOM.hide(`#icons_modal`)
  }
}

async function enter_icons() {
  if (!vars.selected_icon) {
    return
  }

  hide_icons()
  send_reaction(vars.selected_icon, `icon`)
}

function hide_icons() {
  DOM.hide(`#icons_modal`)
}

function up_icons() {
  let icons = DOM.el(`#icons`)
  let children = Array.from(icons.children)
  let visible = children.filter(c => !DOM.is_hidden(c))

  for (let [i, child] of visible.entries()) {
    if (child.classList.contains(`selected`)) {
      if (i > 0) {
        let prev = visible[i - 1]
        child.classList.remove(`selected`)
        prev.classList.add(`selected`)
        vars.selected_icon = prev.textContent
        prev.scrollIntoView({block: `center`})
      }

      break
    }
  }
}

function down_icons() {
  let icons = DOM.el(`#icons`)
  let children = Array.from(icons.children)
  let visible = children.filter(c => !DOM.is_hidden(c))

  for (let [i, child] of visible.entries()) {
    if (child.classList.contains(`selected`)) {
      if (i < (visible.length - 1)) {
        let next = visible[i + 1]
        child.classList.remove(`selected`)
        next.classList.add(`selected`)
        vars.selected_icon = next.textContent
        next.scrollIntoView({block: `center`})
      }

      break
    }
  }
}

function add_reaction(reaction) {
  let r = reaction
  let reactions = DOM.el(`#reactions`)
  DOM.show(reactions)
  let item = DOM.create(`div`, `reaction_item`)

  if (r.mode === `character`) {
    let character = DOM.create(`div`)
    character.textContent = r.value
    character.title = r.title
    item.appendChild(character)
  }
  else if (r.mode === `icon`) {
    let img = DOM.create(`img`)
    img.loading = `lazy`
    img.src = `/static/icons/${r.value}.gif`
    img.title = r.title
    item.appendChild(img)
  }

  let info = DOM.el(`#reaction_info_template`)
  let clone = info.content.cloneNode(true)
  DOM.el(`.uname`, clone).textContent = reaction.uname_str
  DOM.el(`.ago`, clone).textContent = reaction.ago
  item.appendChild(clone)
  let rc = DOM.el(`#reveal_container`)
  DOM.show(rc)

  reactions.appendChild(item)
}

function icons_open() {
  return !DOM.is_hidden(`#icons_modal`)
}

function show_all_icons() {
  let icons = DOM.el(`#icons`)

  for (let child of icons.children) {
    DOM.show(child)
  }
}

function react_character() {
  if (!vars.can_react) {
    react_alert()
    return
  }

  let n = vars.character_reaction_length
  let ns = singplural(`character`, n)
  let char = prompt(`Max ${n} ${ns} (no spaces)`)

  if (!char) {
    return
  }

  char = char.replace(/[;<> ]/g, ``)
  char = char.replace(/https?:\/\//gi, ``)
  char = char.slice(0, n).trim()

  send_reaction(char, `character`)
}

async function send_reaction(text, mode) {
  if (!vars.can_react) {
    return
  }

  let name = vars.name

  let response = await fetch(`/react`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name, text, mode}),
  })

  if (response.ok) {
    let json = await response.json()
    add_reaction(json.reaction)
    window.scrollTo(0, document.body.scrollHeight)
  }
  else {
    print_error(response.status)
  }
}

async function refresh() {
  let name = vars.name

  let response = await fetch(`/refresh`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name}),
  })

  if (response.ok) {
    let json = await response.json()
    apply_update(json.update)
  }
  else {
    print_error(response.status)
  }
}

function apply_update(update) {
  if (update.reactions && update.reactions.length) {
    let c = DOM.el(`#reactions`)
    c.innerHTML = ``

    for (let reaction of update.reactions) {
      add_reaction(reaction)
    }
  }

  vars.title = update.title
  document.title = update.post_title
  DOM.el(`#title`).textContent = update.title || vars.original
  DOM.el(`#views`).textContent = update.views
}

function reveal_reactions() {
  let c = DOM.el(`#reactions`)
  c.classList.toggle(`no_info`)
}