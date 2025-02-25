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
  vars.max_on = false
  vars.max_id = ``
  vars.image_expanded = false

  let delay = 30

  setInterval(function() {
    update_date()
  }, 1000 * delay)

  update_date()

  let edit = DOM.el(`#edit`)

  if (edit) {
    vars.msg_edit = Msg.factory()
    let t = DOM.el(`#template_edit`)
    vars.msg_edit.set(t.innerHTML)

    DOM.ev(`#edit_title`, `click`, () => {
      vars.msg_edit.close()
      edit_title()
    })

    DOM.ev(`#edit_delete`, `click`, () => {
      vars.msg_edit.close()

      let confirm_args = {
        message: `Delete this post ?`,
        callback_yes: () => {
          delete_post()
        },
      }

      confirmbox(confirm_args)
    })

    DOM.ev(edit, `click`, () => {
      vars.msg_edit.show()
    })
  }

  if (vars.mtype.startsWith(`text`)) {
    if (vars.mtype === `text/markdown`) {
      let view = DOM.el(`#markdown`)
      let sample = view.textContent.trim()
      vars.original_markdown = sample

      try {
        let html = marked.parse(
          sample.replace(/[\u200B-\u200F\uFEFF]/g, ``).trim(),
        )

        DOM.el(`#markdown`).innerHTML = html
      }
      catch (e) {
        print_error(e)
      }
    }
    else {
      function guess_mode() {
        let modelist = ace.require(`ace/ext/modelist`)
        let modes = modelist.modes

        for (let mode of modes) {
          if (vars.mtype.includes(mode.name)) {
            return mode.mode
          }
        }

        return `ace/mode/text`
      }

      ace.config.set(`basePath`, `/static/ace`)
      vars.editor = ace.edit(`editor`)
      vars.editor.setTheme(`ace/theme/tomorrow_night_eighties`)
      let mode = guess_mode(vars.sample)
      vars.editor.session.setMode(mode)
      vars.editor.session.setValue(vars.sample, -1)
      vars.editor.setReadOnly(true)
      vars.editor.setShowPrintMargin(false)
    }
  }
  else if (vars.mtype.startsWith(`application`)) {
    if (vars.mtype.includes(`flash`)) {
      start_flash(vars.name)
    }
  }

  let image = DOM.el(`#image`)

  if (image) {
    DOM.ev(image, `click`, () => {
      show_modal_image()
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
      react_icon()
    })
  }

  let r_text = DOM.el(`#react_text`)

  if (r_text) {
    DOM.ev(r_text, `click`, () => {
      react_text()
    })
  }

  let r_bottom = DOM.el(`#lobottomy`)

  if (r_bottom) {
    DOM.ev(r_bottom, `click`, () => {
      window.scrollTo(0, document.body.scrollHeight)
    })
  }

  let r_top = DOM.el(`#totopia`)

  if (r_top) {
    DOM.ev(r_top, `click`, () => {
      window.scrollTo(0, 0)
    })
  }

  if (vars.post_refresh_times > 0) {
    vars.refresh_interval = setInterval(() => {
      refresh()
      vars.refresh_count += 1

      if (vars.refresh_count >= vars.post_refresh_times) {
        clearInterval(vars.refresh_interval)
      }
    }, vars.post_refresh_interval * 1000)
  }

  let copy_all = DOM.el(`#copy_all_text`)

  if (copy_all) {
    DOM.ev(copy_all, `click`, () => {
      copy_all_text()
    })
  }

  let select_all = DOM.el(`#select_all_text`)

  if (select_all) {
    DOM.ev(select_all, `click`, () => {
      select_all_text()
    })
  }

  let video = DOM.el(`#video`)

  if (video) {
    video.muted = true
    video.play()
    video.muted = false
  }

  let max_video = DOM.el(`#max_video`)

  if (max_video) {
    DOM.ev(max_video, `click`, () => {
      toggle_max(`video`)
    })
  }

  let max_editor = DOM.el(`#max_editor`)

  if (max_editor) {
    DOM.ev(max_editor, `click`, () => {
      toggle_max(`editor`)
    })
  }

  let max_markdown = DOM.el(`#max_markdown`)

  if (max_markdown) {
    DOM.ev(max_markdown, `click`, () => {
      toggle_max(`markdown`)
    })
  }

  let max_flash = DOM.el(`#max_flash`)

  if (max_flash) {
    DOM.ev(max_flash, `click`, () => {
      toggle_max(`flash`)
    })
  }

  DOM.ev(window, `resize`, () => {
    if (vars.max_on) {
      resize_max()
    }
  })

  if (vars.image_embed) {
    vars.msg_image = Msg.factory({
      class: `modal_image`,
      disable_content_padding: true,
      before_show: () => {
        reset_modal_image()
      },
    })

    let t = DOM.el(`#template_image`)
    vars.msg_image.set(t.innerHTML)
    let img = DOM.el(`#modal_image`)

    DOM.ev(img, `click`, () => {
      hide_modal_image()
    })

    DOM.ev(img, `wheel`, () => {
      expand_modal_image()
    })
  }

  let reacts = DOM.el(`#reactions`)

  if (reacts) {
    DOM.ev(reacts, `click`, (e) => {
      let el = e.target.closest(`.reaction_item`)
      vars.active_item = el

      if (e.target.classList.contains(`reaction_uname`)) {
        vars.user_opts_username = el.dataset.username
        vars.msg_user_opts.show()
      }
      else if (e.target.classList.contains(`reaction_edit`)) {
        vars.msg_reaction_opts.show()
      }
    })
  }

  fill_reactions()

  let user_opts = DOM.el(`#template_user_opts`)

  if (user_opts) {
    setup_user_opts()
  }

  setup_reaction_opts()

  let uploader = DOM.el(`#uploader`)

  if (uploader) {
    DOM.ev(uploader, `click`, () => {
      vars.user_opts_username = vars.uploader
      vars.msg_user_opts.show()
    })
  }

  let react_btn = DOM.el(`#react_btn`)

  if (react_btn) {
    setup_react_opts()

    DOM.ev(react_btn, `click`, () => {
      vars.msg_react_opts.show()
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
  let prompt_args = {
    placeholder: `Edit Title`,
    value: vars.title || vars.original,
    max: vars.max_title_length,
    callback: async (title) => {
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
    },
  }

  prompt_text(prompt_args)
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
  player.id = `flash`
  player.style.width = `800px`
  player.style.height = `600px`
  let container = DOM.el(`#flash_container`)
  container.appendChild(player)
  player.ruffle().load(`/${vars.file_path}/${file}`)
}

function react_alert() {
  popmsg(`You might have to login to react.`)
}

async function react_icon(id) {
  if (!vars.can_react) {
    react_alert()
    return
  }

  if (!vars.icons_loaded) {
    vars.msg_icons = Msg.factory({
      disable_content_padding: true,
    })

    let t = DOM.el(`#template_icons`)
    vars.msg_icons.set(t.innerHTML)
    await fill_icons()
    add_icon_events()
    vars.icons_loaded = true
  }
  else {
    show_all_icons()
  }

  vars.icons_id = id
  vars.msg_icons.show()
  let input = DOM.el(`#icons_input`)
  input.value = ``
  input.focus()
  select_first_icon()
  DOM.el(`#icons`).scrollTop = 0
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
    vars.msg_icons.close()
  }
}

async function enter_icons() {
  if (!vars.selected_icon) {
    return
  }

  hide_icons()

  if (vars.icons_id) {
    edit_reaction(vars.icons_id, vars.selected_icon, `icon`)
  }
  else {
    send_reaction(vars.selected_icon, `icon`)
  }
}

function hide_icons() {
  vars.msg_icons.close()
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
  let reactions = DOM.el(`#reactions`)
  DOM.show(reactions)
  reactions.appendChild(make_reaction(reaction))
}

function make_reaction(reaction) {
  let r = reaction
  let vitem

  if (r.mode === `text`) {
    vitem = DOM.create(`div`)
    vitem.innerHTML = text_html(r.value)
  }
  else if (r.mode === `icon`) {
    vitem = DOM.create(`img`)
    vitem.loading = `lazy`
    vitem.src = `/static/icons/${r.value}.gif`
    vitem.title = r.value
  }

  if (!vitem) {
    return
  }

  let t = DOM.el(`#template_reaction_item`)
  let item = DOM.create(`div`, `reaction_item`)
  item.innerHTML = t.innerHTML
  let n = vars.max_reaction_name_length
  let name = reaction.uname_str.substring(0, n).trim()
  DOM.el(`.reaction_uname`, item).textContent = name
  DOM.el(`.reaction_value`, item).appendChild(vitem)
  let ago = DOM.el(`.reaction_ago`, item)

  new Tooltip({
    element: ago,
    generate: () => {
      return dateFormat(r.date * 1000, `d mmmm yyyy hh:MM TT`)
    },
  })

  ago.textContent = reaction.ago
  DOM.show(`#to_bottom_container`)
  DOM.show(`#totopia`)
  item.dataset.id = r.id
  item.dataset.username = r.user
  item.dataset.value = r.value
  item.dataset.mode = r.mode
  item.dataset.date = r.date

  if ((r.user === vars.username) || vars.is_admin) {
    DOM.show(DOM.el(`.reaction_edit`, item))
  }

  return item
}

function icons_open() {
  return vars.msg_icons && vars.msg_icons.is_open()
}

function show_all_icons() {
  let icons = DOM.el(`#icons`)

  for (let child of icons.children) {
    DOM.show(child)
  }
}

function get_reaction(id) {
  let reactions = DOM.el(`#reactions`)
  let item = reactions.querySelector(`[data-id="${id}"]`)
  return item
}

function react_text(id) {
  if (!vars.can_react) {
    react_alert()
    return
  }

  let value

  if (id) {
    let r = get_reaction(id)

    if (r.dataset.mode === `text`) {
      value = r.dataset.value
    }
  }
  else {
    value = ``
  }

  let prompt_args = {
    placeholder: `Write a text reaction`,
    max: vars.text_reaction_length,
    multi: true,
    value,
    callback: (text) => {
      if (!text) {
        return
      }

      let n = vars.text_reaction_length
      text = remove_multiple_empty_lines(text)
      text = replace_urls(text)
      text = Array.from(text).slice(0, n).join(``)

      if (contains_url(text)) {
        popmsg(`URLs are not allowed.`)
        return true
      }

      if (id) {
        edit_reaction(id, text, `text`)
      }
      else {
        send_reaction(text, `text`)
      }
    },
  }

  prompt_text(prompt_args)
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

async function edit_reaction(id, text, mode) {
  if (!vars.can_react) {
    return
  }

  let response = await fetch(`/edit_reaction`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({id, text, mode}),
  })

  if (response.ok) {
    let json = await response.json()
    modify_reaction(json.reaction)
  }
  else {
    print_error(response.status)
  }
}

function modify_reaction(reaction) {
  let item = get_reaction(reaction.id)

  if (!item) {
    return
  }

  new_item = make_reaction(reaction)
  item.replaceWith(new_item)
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

function show_modal_image() {
  vars.msg_image.show()
}

function hide_modal_image() {
  vars.msg_image.close()
}

function toggle_modal_image() {
  vars.msg_image.toggle()
}

function copy_all_text() {
  copy_to_clipboard(get_text_value())
}

function select_all_text() {
  if (vars.editor) {
    vars.editor.selectAll()
    return
  }

  let markdown = DOM.el(`#markdown`)

  if (markdown) {
    select_all(markdown)
  }
}

function get_text_value() {
  if (vars.editor) {
    return vars.editor.getValue()
  }

  let markdown = DOM.el(`#mardkwon`)

  if (markdown) {
    return vars.original_markdown
  }
}

function toggle_max(what) {
  let el = DOM.el(`#${what}`)
  let details = DOM.el(`#details`)
  vars.max_on = !vars.max_on
  vars.max_id = what

  if (vars.max_on) {
    resize_max()
    DOM.hide(details)
    el.classList.add(`max`)
  }
  else {
    DOM.show(details)
    el.classList.remove(`max`)
  }
}

function resize_max() {
  let el = DOM.el(`#${vars.max_id}`)
  let w_width = window.innerWidth
  let w_height = window.innerHeight
  let v_rect = el.getBoundingClientRect()
  let v_width = w_width - v_rect.left - 20
  let v_height = w_height - v_rect.top - 20
  set_css_var(`max_width`, `${v_width}px`)
  set_css_var(`max_height`, `${v_height}px`)
}

function add_icon_events() {
  let input = DOM.el(`#icons_input`)
  let container = DOM.el(`#icons`)

  DOM.ev(input, `input`, () => {
    filter_icons()
  })

  DOM.ev(input, `keydown`, (e) => {
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

  DOM.ev(container, `click`, (e) => {
    if (e.target.closest(`.icon_item`)) {
      let item = e.target.closest(`.icon_item`)
      vars.selected_icon = item.dataset.icon
      enter_icons()
    }
  })
}

async function fill_icons() {
  let container = DOM.el(`#icons`)
  let response = await fetch(`/get_icons`)

  if (!response.ok) {
    print_error(response.status)
    return
  }

  let json = await response.json()
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
}

function expand_modal_image() {
  if (vars.image_expanded) {
    return
  }

  let c = DOM.el(`#modal_image_container`)
  c.classList.add(`expanded`)
  vars.image_expanded = true
}

function reset_modal_image() {
  if (!vars.image_expanded) {
    return
  }

  let c = DOM.el(`#modal_image_container`)
  c.classList.remove(`expanded`)
  vars.image_expanded = false
}

function fill_reactions() {
  for (let reaction of vars.reactions) {
    add_reaction(reaction)
  }
}

function delete_reaction(id) {
  let confirm_args = {
    message: `Delete this reaction ?`,
    callback_yes: () => {
      do_delete_reaction(id)
    },
  }

  confirmbox(confirm_args)
}

async function do_delete_reaction(id) {
  let response = await fetch(`/delete_reaction`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({id}),
  })

  if (response.ok) {
    remove_reaction(id)
  }
  else {
    print_error(response.status)
  }
}

function remove_reaction(id) {
  let reactions = DOM.el(`#reactions`)
  let item = reactions.querySelector(`[data-id="${id}"]`)

  if (item) {
    item.remove()
  }

  if (!reactions.children.length) {
    DOM.hide(reactions)
    DOM.hide(`#to_bottom_container`)
    DOM.hide(`#totopia`)
  }
}

function replace_urls(text) {
  let here = window.location.origin
  let re = new RegExp(`${here}/post/([0-9A-Za-z]+)/?$`, `g`)
  text = text.replace(re, `/post/$1`)
  re = /https?:\/\/([a-z]{2,3})\.wikipedia\.org\/wiki\/([0-9A-Za-z_()#-]+)\/?$/g
  text = text.replace(re, `/wiki/$2`)
  re = /https?:\/\/www\.youtube\.com\/watch\?v=([0-9A-Za-z_-]+)\/?$/g
  text = text.replace(re, `/yt/$1`)
  re = /https?:\/\/youtu\.be\/([0-9A-Za-z_-]+)\/?$/g
  text = text.replace(re, `/yt/$1`)
  re = /https?:\/\/github\.com\/([0-9A-Za-z_-]+)\/([0-9A-Za-z_-]+)\/?$/g
  return text.replace(re, `/github/$1/$2`)
}

function text_html(text) {
  // Remove < and > to prevent XSS
  text = text.replace(/</g, `&lt;`)
  text = text.replace(/>/g, `&gt;`)

  // Markdown
  text = parse_markdown(text)

  // Internal posts
  let re = new RegExp(`/post/([0-9A-Za-z]+)`, `gi`)
  text = text.replace(re, `<a href="/post/$1">Post: $1</a>`)

  // Wikipedia
  re = /\/wiki\/([0-9A-Za-z_()-]+)(#[0-9A-Za-z_()-]+)?\/?/gi

  text = text.replace(re, (match, g1, g2) => {
    let u = g1
    let s = decodeURIComponent(g1)

    if (g2) {
      u += g2
      s += decodeURIComponent(g2)
    }

    return `<a href="https://wikipedia.org/wiki/${u}">Wiki: ${s}</a>`
  })

  // YouTube
  re = /\/yt\/([0-9A-Za-z_-]+)\/?/gi
  text = text.replace(re, `<a href="https://www.youtube.com/watch?v=$1">YT: $1</a>`)

  // GitHub
  re = /\/github\/([0-9A-Za-z_-]+)\/([0-9A-Za-z_-]+)\/?/gi
  text = text.replace(re, `<a href="https://github.com/$1/$2">GH: $1/$2</a>`)
  return text
}

function on_image_load() {
  let img = DOM.el(`#image`)

  if (img) {
    let w = img.naturalWidth
    let h = img.naturalHeight
    DOM.el(`#resolution`).textContent = `${w} x ${h}`
    DOM.show(`#resolution_container`)
  }
}