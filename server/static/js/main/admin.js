App.init = () => {
  App.selected_items = []
  App.last_checkbox = null
  App.sample_name = ``

  App.key_events()
  App.pointer_events()

  let refresh_btn = DOM.el(`#refresh`)

  if (refresh_btn) {
    DOM.ev(refresh_btn, `click`, () => {
      App.refresh()
    })

    DOM.ev(refresh_btn, `auxclick`, () => {
      App.refresh(true)
    })
  }

  let random_btn = DOM.el(`#random`)

  if (random_btn) {
    DOM.ev(random_btn, `click`, () => {
      App.random_page()
    })

    DOM.ev(random_btn, `auxclick`, () => {
      App.random_page(true)
    })
  }

  let del_sel = DOM.el(`#delete_selected`)

  if (del_sel) {
    DOM.ev(del_sel, `click`, () => {
      App.delete_selected()
    })
  }

  App.setup_edit()

  let page_select = DOM.el(`#page_select`)

  if (page_select) {
    App.fill_page_select(page_select)

    DOM.ev(page_select, `change`, () => {
      App.on_page_select_change()
    })
  }

  let media_select = DOM.el(`#media_select`)

  if (media_select) {
    App.set_active_media_select()

    DOM.ev(media_select, `change`, () => {
      App.on_media_select_change(media_select)
    })
  }

  let filter = DOM.el(`#filter`)

  if (filter) {
    DOM.ev(filter, `input`, () => {
      App.do_filter()
    })

    filter.focus()
  }

  let cb = DOM.el(`#checkbox`)

  if (cb) {
    DOM.ev(cb, `click`, () => {
      App.toggle_select()
    })
  }

  let add = DOM.el(`#add`)

  if (add) {
    DOM.ev(add, `click`, () => {
      App.location(`/edit_user`)
    })
  }

  App.setup_pages()

  let del_all = DOM.el(`#delete_all`)

  if (del_all) {
    DOM.ev(del_all, `click`, () => {
      App.delete_all()
    })
  }

  let menu_opts = DOM.el(`#template_menu_opts`)

  if (menu_opts) {
    App.setup_menu_opts()

    let menu = DOM.el(`#menu`)

    if (menu) {
      DOM.evs(menu, [`click`, `auxclick`], (e) => {
        App.show_menu()
      })
    }
  }

  let user_opts = DOM.el(`#template_user_opts`)

  if (user_opts) {
    App.setup_user_opts()
  }

  for (let el of DOM.els(`.reaction_value`)) {
    let v = el.innerText
    el.innerHTML = App.text_html(v, false)
  }

  for (let el of DOM.els(`.last_reaction`)) {
    let v = el.innerText
    el.innerHTML = App.text_html(v, false)
  }

  let clear_filter_btn = DOM.el(`#clear_filter`)

  if (clear_filter_btn) {
    DOM.ev(clear_filter_btn, `click`, () => {
      App.clear_filter()
    })
  }

  App.setup_sample()
}

App.goto_page = (page, new_tab = false) => {
  let psize = App.page_size
  let url = new URL(window.location.href)
  url.searchParams.set(`page`, page)
  url.searchParams.set(`page_size`, psize)

  if (App.used_user_id) {
    url.searchParams.set(`user_id`, App.used_user_id)
  }

  App.goto_url(url.href, new_tab)
}

App.fill_page_select = (page_select) => {
  function add_option(n, selected = false) {
    let option = document.createElement(`option`)
    option.value = n
    option.innerText = n
    option.selected = selected
    page_select.appendChild(option)
  }

  function add_separator() {
    let sep = document.createElement(`hr`)
    page_select.appendChild(sep)
  }

  add_option(`Default`, App.def_page_size)
  add_separator()

  let nums = [5, 10, 20, 50, 100, 200, 500, 1000]

  for (let n of nums) {
    let selected = false

    if (!App.def_page_size) {
      if (App.page_size === n.toString()) {
        selected = true
      }
    }

    add_option(n, selected)
  }

  add_separator()
  add_option(`All`, App.page_size === `all`)
}

App.on_page_select_change = () => {
  App.do_search()
}

App.delete_posts = () => {
  if (App.selected_items.length === 0) {
    App.popmsg(`No items selected`)
    return
  }

  let size = 0

  for (let post of App.selected_items) {
    size += parseFloat(post.dataset.size)
  }

  size = Math.round(size * 100) / 100
  let s = App.singplural(`post`, App.selected_items.length)

  let confirm_args = {
    message: `Delete ${App.selected_items.length} ${s} (${App.size_string(size)})`,
    callback_yes: () => {
      let posts = []

      for (let post of App.selected_items) {
        posts.push(post.dataset.post_id)
      }

      App.delete_selected_posts(posts)
    },
  }

  App.confirmbox(confirm_args)
}

App.delete_selected_posts = async (ids) => {
  let response = await fetch(`/delete_posts`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids}),
  })

  if (response.ok) {
    App.remove_posts(ids)
  }
  else {
    App.feedback(response)
  }
}

App.remove_posts = (posts) => {
  for (let post of posts) {
    let el = DOM.el(`.item[data-post_id="${post}"]`)

    if (el) {
      el.remove()
    }
  }
}

App.delete_all_posts = async () => {
  let response = await fetch(`/delete_all_posts`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify(),
  })

  if (response.ok) {
    App.location(`/admin/posts`)
  }
  else {
    App.feedback(response)
  }
}

App.select_all = () => {
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    checkbox.checked = true
  }

  DOM.el(`#checkbox`).checked = true
}

App.unselect_all = () => {
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    checkbox.checked = false
  }

  DOM.el(`#checkbox`).checked = false
}

App.size_string = (size) => {
  size /= 1000

  if (size < 1000) {
    return `${size.toFixed(2)} kb`
  }

  size /= 1000

  if (size < 1000) {
    return `${size.toFixed(2)} mb`
  }

  size /= 1000
  return `${size.toFixed(2)} gb`
}

App.do_search = (query = ``, use_media_type = true, new_tab = false) => {
  if (!query) {
    query = DOM.el(`#filter`).value.trim()
  }

  let url = new URL(window.location.href)

  if (use_media_type) {
    let media_type = App.get_media_type()

    if (media_type) {
      url.searchParams.set(`media_type`, media_type)
    }
  }
  else {
    url.searchParams.delete(`media_type`)
  }

  let page_size = App.get_page_size()

  if (page_size) {
    url.searchParams.set(`page_size`, page_size)
  }

  url.searchParams.delete(`page`)
  url.searchParams.set(`query`, App.encode_uri(query))
  App.goto_url(url.href, new_tab)
}

App.edit_post_title = (el) => {
  let items = App.get_selected()

  if (items.length === 0) {
    App.popmsg(`No items selected`)
    return
  }

  let ids = items.map(x => x.dataset.post_id)
  App.msg_post_edit.close()

  let prompt_args = {
    placeholder: `Enter new title`,
    max: App.max_title_length,
    callback: async (title) => {
      let response = await fetch(`/edit_title`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({ids, title}),
      })

      if (response.ok) {
        App.refresh()
      }
      else {
        App.feedback(response)
      }
    },
  }

  App.prompt_text(prompt_args)
}

App.edit_post_privacy = (privacy) => {
  let items = App.get_selected()

  if (items.length === 0) {
    App.popmsg(`No items selected`)
    return
  }

  let ids = items.map(x => x.dataset.post_id)
  App.msg_post_edit.close()
  let message = `Make selected posts ${privacy}`

  let confirm_args = {
    message,
    callback_yes: async () => {
      let response = await fetch(`/edit_privacy`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({ids, privacy}),
      })

      if (response.ok) {
        App.refresh()
      }
      else {
        App.feedback(response)
      }
    },
  }

  App.confirmbox(confirm_args)
}

App.toggle_select = () => {
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    if (!checkbox.checked) {
      App.select_all()
      return
    }
  }

  App.unselect_all()
}

App.get_selected = () => {
  let items = []
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    if (checkbox.checked) {
      items.push(checkbox.closest(`.item`))
    }
  }

  return items
}

App.delete_selected = () => {
  let items = App.get_selected()

  if (items.length === 0) {
    App.popmsg(`No items selected`)
    return
  }

  App.selected_items = items

  if (App.mode === `admin_users`) {
    App.delete_users()
  }
  else if (App.mode === `admin_posts`) {
    App.delete_posts()
  }
  else if (App.mode === `admin_reactions`) {
    App.delete_reactions()
  }
}

App.delete_users = () => {
  if (App.selected_items.length === 0) {
    App.popmsg(`No items selected`)
    return
  }

  let size = 0

  for (let user of App.selected_items) {
    size += parseFloat(user.dataset.size)
  }

  size = Math.round(size * 100) / 100
  let s = App.singplural(`user`, App.selected_items.length)

  let confirm_args = {
    message: `Delete ${App.selected_items.length} ${s}`,
    callback_yes: () => {
      let users = []

      for (let user of App.selected_items) {
        users.push(parseInt(user.dataset.user_id))
      }

      App.delete_selected_users(users)
    },
  }

  App.confirmbox(confirm_args)
}

App.delete_selected_users = async (ids) => {
  let response = await fetch(`/delete_users`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids}),
  })

  if (response.ok) {
    App.remove_users(ids)
  }
  else {
    App.feedback(response)
  }
}

App.remove_users = (ids) => {
  for (let id of ids) {
    let el = DOM.el(`.item[data-user_id="${id}"]`)

    if (el) {
      el.remove()
    }
  }
}

App.delete_normal_users = async () => {
  let response = await fetch(`/delete_normal_users`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify(),
  })

  if (response.ok) {
    App.location(`/admin/users`)
  }
  else {
    App.feedback(response)
  }
}

App.sort_action = (what, desc = false, page = false) => {
  if (page) {
    let container = DOM.el(`#items_container`)
    let items = App.get_items()

    items.sort((a, b) => {
      let value_a = a.dataset[what]
      let value_b = b.dataset[what]

      // Handle undefined/null values
      if (!value_a && !value_b) return 0
      if (!value_a) return desc ? -1 : 1
      if (!value_b) return desc ? 1 : -1

      // Try to parse as numbers first
      let num_a = parseFloat(value_a)
      let num_b = parseFloat(value_b)

      if (!isNaN(num_a) && !isNaN(num_b)) {
        return desc ? num_b - num_a : num_a - num_b
      }

      // Fall back to string comparison
      let str_a = value_a.toString().toLowerCase()
      let str_b = value_b.toString().toLowerCase()
      return desc ? str_b.localeCompare(str_a) : str_a.localeCompare(str_b)
    })

    container.innerHTML = ``

    for (let item of items) {
      container.appendChild(item)
    }
  }
  else {
    if (desc) {
      what = what + `_desc`
    }
    else {
      what = what + `_asc`
    }

    let ms = App.mode_string()
    App.location(`/${ms}?sort=${what}`)
  }
}

App.do_sort = (what) => {
  App.sort_what = what
  App.setup_sort_opts(true)
}

App.mod_user = (what, value, vtype) => {
  let items = App.get_selected()

  if (!items.length) {
    return
  }

  let s = App.singplural(`user`, items.length)
  let w = App.capitalize(what)

  let confirm_args = {
    message: `Modify ${items.length} ${s} (${w})`,
    callback_yes: () => {
      App.msg_user_edit.close()
      App.do_mod_user(items, what, value, vtype)
    },
  }

  App.confirmbox(confirm_args)
}

App.do_mod_user = async (items, what, value, vtype) => {
  let ids = items.map(x => x.dataset.user_id)

  let response = await fetch(`/mod_user`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids, what, value, vtype}),
  })

  if (response.ok) {
    App.refresh()
  }
  else {
    App.feedback(response)
  }
}

App.delete_all = () => {
  if (App.mode === `admin_users`) {
    App.delete_all_items(`users`, () => {
      App.delete_normal_users()
    })
  }
  else if (App.mode === `admin_posts`) {
    App.delete_all_items(`posts`, () => {
      App.delete_all_posts()
    })
  }
  else if (App.mode === `admin_reactions`) {
    App.delete_all_items(`reactions`, () => {
      App.delete_all_reactions()
    })
  }
}

App.get_items = () => {
  return DOM.els(`.item`, DOM.el(`#items`))
}

App.filter_value = () => {
  let filter = DOM.el(`#filter`)
  return filter.value.trim()
}

App.do_filter = () => {
  function clean(s) {
    s = s.toLowerCase()
    return s.replace(/[\s:]/g, ``).trim()
  }

  let items = App.get_items()
  let value = clean(App.filter_value().toLowerCase())

  for (let item of items) {
    let post = item.dataset.post
    let ago = item.dataset.ago
    let date = item.dataset.date
    let size = item.dataset.size_str
    let title = item.dataset.title
    let original = item.dataset.original
    let uploader = item.dataset.uploader
    let views = item.dataset.views
    let listed = item.dataset.listed
    let mtype = item.dataset.mtype
    let uname = item.dataset.username
    let ext = item.dataset.ext
    let username = item.dataset.username
    let rpm = item.dataset.rpm
    let max_size = item.dataset.max_size
    let mark = item.dataset.mark
    let reg_date = item.dataset.reg_date
    let last_date = item.dataset.last_date
    let admin = item.dataset.admin
    let lister = item.dataset.lister
    let reader = item.dataset.reader
    let mage = item.dataset.mage
    let value_ = item.dataset.value
    let num_posts = item.dataset.num_posts
    let num_reactions = item.dataset.num_reactions
    let full = item.dataset.full
    let privacy = item.dataset.privacy
    let regdate_ago = item.dataset.regdate_ago
    let lastdate_ago = item.dataset.lastdate_ago
    let description = item.dataset.description

    let opts = [
      post, ago, date, size, title, original, uploader, views, mage,
      listed, mtype, uname, ext, username, rpm, max_size, mark, full, lister,
      reg_date, last_date, admin, reader, value_, num_posts, num_reactions,
      privacy, regdate_ago, lastdate_ago, description,
    ]

    opts = opts.filter(x => x)
    opts = opts.map(x => clean(x))

    if (opts.some(x => x.includes(value))) {
      DOM.show(item)
    }
    else {
      DOM.hide(item)
    }
  }
}

App.mode_string = () => {
  let split = App.mode.split(`_`)
  return split.join(`/`)
}

App.delete_reactions = () => {
  if (App.selected_items.length === 0) {
    App.popmsg(`No items selected`)
    return
  }

  let size = 0

  for (let reaction of App.selected_items) {
    size += parseFloat(reaction.dataset.size)
  }

  let s = App.singplural(`reaction`, App.selected_items.length)

  let confirm_args = {
    message: `Delete ${App.selected_items.length} ${s}`,
    callback_yes: () => {
      let reactions = []

      for (let reaction of App.selected_items) {
        reactions.push(parseInt(reaction.dataset.id))
      }

      App.delete_selected_reactions(reactions)
    },
  }

  App.confirmbox(confirm_args)
}

App.delete_selected_reactions = async (ids) => {
  let response = await fetch(`/delete_reactions`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({ids}),
  })

  if (response.ok) {
    App.remove_reactions(ids)
  }
  else {
    App.feedback(response)
  }
}

App.remove_reactions = (reactions) => {
  for (let id of reactions) {
    let el = DOM.el(`.item[data-id="${id}"]`)

    if (el) {
      el.remove()
    }
  }
}

App.delete_all_reactions = async () => {
  let response = await fetch(`/delete_all_reactions`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify(),
  })

  if (response.ok) {
    App.location(`/admin/reactions`)
  }
  else {
    App.feedback(response)
  }
}

App.show_menu = () => {
  App.msg_show(`menu`)
}

App.filter_focused = () => {
  let filter = DOM.el(`#filter`)
  return filter && (document.activeElement === filter)
}

App.on_checkbox_click = (e) => {
  if (e.shiftKey && App.last_checkbox) {
    let checked = App.last_checkbox.checked
    let boxes = DOM.els(`.select_checkbox`)
    let selected = [e.target]
    let waypoints = 0

    for (let box of boxes) {
      if (box === e.target) {
        waypoints += 1

        if (waypoints >= 2) {
          break
        }
      }
      else if (box === App.last_checkbox) {
        waypoints += 1

        if (waypoints >= 2) {
          break
        }
      }
      else if (waypoints === 1) {
        selected.push(box)
      }
    }

    for (let box of selected) {
      box.checked = checked
    }
  }

  App.last_checkbox = e.target
}

App.set_filter = (value) => {
  let filter = DOM.el(`#filter`)
  filter.value = value
  App.do_filter()
}

App.clear_filter = () => {
  App.set_filter(``)
  App.focus_filter()
}

App.focus_filter = () => {
  let filter = DOM.el(`#filter`)
  filter.focus()
}

App.setup_edit = () => {
  let edit = DOM.el(`#edit`)

  if (!edit) {
    return
  }

  if (App.mode === `admin_users`) {
    App.setup_user_edit_opts()

    DOM.ev(edit, `click`, () => {
      if (App.get_selected().length > 0) {
        App.msg_show(`user_edit`)
      }
      else {
        App.popmsg(`No users are selected`)
      }
    })
  }
  else if (App.mode === `admin_posts`) {
    App.setup_post_edit_opts()

    DOM.ev(edit, `click`, () => {
      if (App.get_selected().length > 0) {
        App.msg_show(`post_edit`)
      }
      else {
        App.popmsg(`No posts are selected`)
      }
    })
  }
}

App.key_events = () => {
  let filter = DOM.el(`#filter`)

  DOM.ev(document, `keydown`, (e) => {
    if (e.key === `Enter`) {
      if (App.no_mod(e)) {
        if (App.filter_focused()) {
          App.do_search()
        }
      }
    }
    else if (e.key === `Escape`) {
      if (App.no_mod(e)) {
        if (App.sample_open()) {
          App.close_sample()
        }
        else if (filter.value) {
          filter.value = ``
          App.do_filter()
        }
        else {
          App.focus_table()
        }
      }
    }
  })

  DOM.ev(document, `keyup`, (e) => {
    if (e.key === `ArrowLeft`) {
      if (App.modal_open()) {
        return
      }

      if (App.no_mod(e)) {
        if (App.sample_open()) {
          App.next_sample(`prev`)
        }
        else if (!App.filter_value()) {
          App.prev_page()
        }
      }
    }
    else if (e.key === `ArrowRight`) {
      if (App.modal_open()) {
        return
      }

      if (App.no_mod(e)) {
        if (App.sample_open()) {
          App.next_sample(`next`)
        }
        else if (!App.filter_value()) {
          App.next_page()
        }
      }
    }
  })
}

App.pointer_events = () => {
  DOM.ev(document, `click`, async (e) => {
    App.doc_click(e, `click`)
  })

  DOM.ev(document, `auxclick`, async (e) => {
    if (e.button === 1) {
      App.doc_click(e, `auxclick`)
    }
  })

  DOM.ev(`#items`, `wheel`, (e) => {
    if (e.target.classList.contains(`sample`)) {
      let direction = e.deltaY > 0 ? `down` : `up`
      App.scroll_text(direction)
      e.stopPropagation()
      e.preventDefault()
    }
  })
}

App.setup_pages = () => {
  let prev_page = DOM.el(`#prev_page`)

  if (prev_page) {
    DOM.ev(prev_page, `click`, () => {
      App.prev_page()
    })

    DOM.ev(prev_page, `auxclick`, () => {
      App.prev_page(true)
    })
  }

  let next_page = DOM.el(`#next_page`)

  if (next_page) {
    DOM.ev(next_page, `click`, () => {
      App.next_page()
    })

    DOM.ev(next_page, `auxclick`, () => {
      App.next_page(true)
    })
  }
}

App.refresh = (new_tab = false) => {
  let ms = App.mode_string()
  let url = `/${ms}`
  App.goto_url(url, new_tab)
}

App.setup_sample_image = () => {
  let img = DOM.el(`#sample_image`)

  DOM.ev(img, `load`, () => {
    App.hide_sample_media(`image`)
  })

  DOM.ev(img, `error`, () => {
    DOM.hide(img)
  })

  DOM.ev(img, `dblclick`, () => {
    App.open_sample()
  })
}

App.setup_sample_video = () => {
  let video = DOM.el(`#sample_video`)

  DOM.ev(video, `play`, () => {
    App.hide_sample_media(`video`)
  })

  DOM.ev(video, `error`, () => {
    DOM.hide(video)
  })

  DOM.ev(video, `dblclick`, () => {
    App.open_sample()
  })
}

App.show_sample_image = (path, title = ``) => {
  App.hide_sample_media()
  App.set_sample_title(title)
  DOM.el(`#sample_image`).src = path
}

App.show_sample_video = (path, title) => {
  App.hide_sample_media()
  App.set_sample_title(title)
  let video = DOM.el(`#sample_video`)
  video.src = path
  video.play()
}

App.show_sample_text = async (path, title = ``) => {
  App.hide_sample_media()
  App.set_sample_title(title)
  let response = await fetch(path)

  if (response.ok) {
    App.hide_sample_media(`text`)
    let text = await response.text()
    DOM.el(`#sample_text`).textContent = text
  }
  else {
    App.feedback(response)
  }
}

App.show_sample = async (item, from = `normal`) => {
  let name = item.dataset.post

  if (App.sample_name === name) {
    if (from === `normal`) {
      App.close_sample()
    }

    return
  }

  App.sample_name = name
  let title = item.dataset.title || item.dataset.original || item.dataset.full
  App.hide_sample_media()
  App.set_sample_title(title)
  DOM.show(`#sample_container`)
  App.check_sample_buttons()

  let response = await fetch(`/get_sample`, {
    method: `POST`,
    headers: {
      "Content-Type": `application/json`,
    },
    body: JSON.stringify({name}),
  })

  let json = await App.json(response)

  if (response.ok) {
    if (json.ext === `jpg`) {
      App.show_sample_image(json.path, title)
    }
    else if (json.ext === `mp3`) {
      App.show_sample_video(json.path, title)
    }
    else if (json.ext === `txt`) {
      App.show_sample_text(json.path, title)
    }
  }
  else {
    App.hide_sample_media()
    App.set_sample_title(`No Sample | ${title}`)
  }
}

App.scroll_text = (direction) => {
  let text = DOM.el(`#text_container`)

  if (!text) {
    return
  }

  if (direction === `up`) {
    text.scrollTop -= 25
  }
  else {
    text.scrollTop += 25
  }
}

App.close_sample = () => {
  App.hide_sample_media()
  DOM.el(`#sample_title`).textContent = ``
  DOM.hide(`#sample_container`)
  App.sample_name = ``
}

App.on_media_select_change = () => {
  App.do_search()
}

App.set_active_media_select = () => {
  let media_select = DOM.el(`#media_select`)

  if (media_select) {
    let value = App.media_type || `all`
    media_select.value = value
  }
}

App.get_page_size = () => {
  let page_select = DOM.el(`#page_select`)

  if (!page_select) {
    return ``
  }

  let value = page_select.value
  let psize

  if (value === `-`) {
    return
  }

  if (value === `All`) {
    psize = `all`
  }
  else if (value === `Default`) {
    psize = `default`
  }
  else {
    psize = parseInt(value)
  }

  return psize
}

App.get_media_type = () => {
  let select = DOM.el(`#media_select`)

  if (!select) {
    return ``
  }

  return select.value
}

App.open_sample = (blank = false) => {
  if (blank) {
    App.open_tab(`/post/${App.sample_name}`)
  }
  else {
    App.location(`/post/${App.sample_name}`)
  }
}

App.setup_sample = () => {
  DOM.ev(`#sample_title`, `click`, () => {
    App.open_sample()
  })

  DOM.ev(`#sample_title`, `auxclick`, () => {
    App.open_sample(true)
  })

  DOM.ev(`#sample_prev`, `click`, () => {
    App.next_sample(`prev`)
  })

  DOM.ev(`#sample_next`, `click`, () => {
    App.next_sample(`next`)
  })

  DOM.ev(`#sample_close`, `click`, () => {
    App.close_sample()
  })

  App.setup_sample_image()
  App.setup_sample_video()
}

App.next_sample = (dir = `next`, just_check = false) => {
  let items = App.get_items()

  for (let [i, item] of items.entries()) {
    let name = item.dataset.post

    if (name === App.sample_name) {
      if (dir === `prev`) {
        if (i === 0) {
          return false
        }
      }
      else if (dir === `next`) {
        if (i === items.length - 1) {
          return false
        }
      }

      let next

      if (dir === `prev`) {
        next = items.at(i - 1)
      }
      else if (dir === `next`) {
        next = items.at(i + 1)
      }

      if (next) {
        if (next.dataset.post === App.sample_name) {
          continue
        }

        if (!just_check) {
          App.show_sample(next, dir)
        }

        return true
      }
    }
  }

  return false
}

App.hide_sample_media = (except = ``) => {
  if (except !== `image`) {
    let img = `#sample_image`
    img.src = ``
    DOM.hide(img)
  }

  if (except !== `video`) {
    let video = DOM.el(`#sample_video`)
    DOM.hide(video)
    video.pause()
    video.currentTime = 0
  }

  if (except !== `text`) {
    let text = DOM.el(`#sample_text`)
    text.textContent = ``
    DOM.hide(text)
  }

  if (except) {
    DOM.hide(`#sample_loading`)
    DOM.show(`#sample_${except}`)
  }
  else {
    DOM.show(`#sample_loading`)
  }
}

App.set_sample_title = (title) => {
  let el = DOM.el(`#sample_title`)
  el.textContent = title
}

App.sample_open = () => {
  return App.sample_name
}

App.prev_page = (open_tab = false) => {
  if (App.page > 1) {
    App.goto_page(App.page - 1, open_tab)
  }
}

App.next_page = (open_tab = false) => {
  if (App.next_page) {
    App.goto_page(App.page + 1, open_tab)
  }
}

App.doc_click = (e, mode) => {
  let item = e.target.closest(`.item`)
  App.active_item = item

  if (e.target.classList.contains(`select_checkbox`)) {
    App.on_checkbox_click(e)
  }
  else if (e.target.classList.contains(`admin_user`)) {
    App.user_opts_user_id = item.dataset.user_id
    App.msg_show(`user`)
  }
  else if (e.target.classList.contains(`mtype`)) {
    let mtype = e.target.textContent
    App.do_search(mtype, false, mode === `auxclick`)
  }
  else if (e.target.closest(`.sample`)) {
    App.show_sample(item)
  }
  else if (e.target.closest(`.header_text`)) {
    let sort = e.target.dataset.sort

    if (sort) {
      App.do_sort(sort)
    }
  }
  else if (e.target.closest(`#sample_container`)) {
    // Do nothing
  }
  else {
    App.close_sample()
  }
}

App.check_sample_buttons = () => {
  let prev = App.next_sample(`prev`, true)
  let next = App.next_sample(`next`, true)

  if (prev) {
    DOM.el(`#sample_prev`).classList.remove(`disabled`)
  }
  else {
    DOM.el(`#sample_prev`).classList.add(`disabled`)
  }

  if (next) {
    DOM.el(`#sample_next`).classList.remove(`disabled`)
  }
  else {
    DOM.el(`#sample_next`).classList.add(`disabled`)
  }
}

App.focus_table = () => {
  DOM.el(`#items`).focus()
}

App.delete_all_items = (what, func) => {
  App.double_confirm(`Delete ALL ${what} ?`, func)
}

App.random_page = () => {
  App.show_random(`page`)
}

App.do_random_page = (media_type, new_tab = false) => {
  let ms = App.mode_string()
  let url = new URL(`/${ms}?random=true`, window.location.origin)

  if (media_type) {
    url.searchParams.set(`media_type`, media_type)
  }

  App.goto_url(url.href, new_tab)
}