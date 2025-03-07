window.onload = () => {
  App.init()
}

App.init = () => {
  App.selected_items = []
  App.last_checkbox = null

  App.key_events()
  App.click_events()

  let refresh_btn = DOM.el(`#refresh`)

  if (refresh_btn) {
    DOM.ev(refresh_btn, `click`, () => {
      App.refresh()
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
      App.on_page_select_change(page_select)
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
      DOM.ev(menu, `click`, (e) => {
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
}

App.goto_page = (page) => {
  let psize = App.page_size
  let url = new URL(window.location.href)
  url.searchParams.set(`page`, page)
  url.searchParams.set(`page_size`, psize)

  if (App.used_user_id) {
    url.searchParams.set(`user_id`, App.used_user_id)
  }

  window.location.href = url.href
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

App.on_page_select_change = (page_select) => {
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

  let url = new URL(window.location.href)
  url.searchParams.set(`page_size`, psize)
  window.location.href = url.href
}

App.delete_posts = () => {
  if (App.selected_items.length === 0) {
    return
  }

  let size = 0

  for (let post of App.selected_items) {
    size += parseFloat(post.dataset.size)
  }

  size = Math.round(size * 100) / 100
  let s = App.singplural(`post`, App.selected_items.length)

  let confirm_args = {
    message: `Delete ${App.selected_items.length} ${s} (${App.size_string(size)}) ?`,
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
  try {
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
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
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
  try {
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
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
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

App.do_search = (query = ``) => {
  if (!query) {
    query = DOM.el(`#filter`).value.trim()
  }

  if (!query) {
    App.refresh()
    return
  }

  let ms = App.mode_string()

  if (query) {
    App.location(`/${ms}?query=${App.encode_uri(query)}`)
  }
  else {
    App.location(`/${ms}`)
  }
}

App.edit_post_title = (el) => {
  App.msg_post_edit.close()
  let t = el.dataset.title
  let o = el.dataset.original
  let current = t || o

  let prompt_args = {
    placeholder: `Enter new title`,
    value: current,
    max: App.max_title_length,
    callback: async (title) => {
      let post_id = el.dataset.post_id

      let response = await fetch(`/edit_title`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({post_id, title}),
      })

      if (response.ok) {
        el.dataset.title = title
        DOM.el(`.title`, el).innerText = title || o
      }
      else {
        App.print_error(response.status)
      }
    },
  }

  App.prompt_text(prompt_args)
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
    return
  }

  let size = 0

  for (let user of App.selected_items) {
    size += parseFloat(user.dataset.size)
  }

  size = Math.round(size * 100) / 100
  let s = App.singplural(`user`, App.selected_items.length)

  let confirm_args = {
    message: `Delete ${App.selected_items.length} ${s} ?`,
    callback_yes: () => {
      let users = []

      for (let user of App.selected_items) {
        users.push(user.dataset.user_id)
      }

      App.delete_selected_users(users)
    },
  }

  App.confirmbox(confirm_args)
}

App.delete_selected_users = async (ids) => {
  try {
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
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
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
  try {
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
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
  }
}

App.sort_action = (what, desc = false) => {
  if (desc) {
    what = what + `_desc`
  }

  let ms = App.mode_string()
  App.location(`/${ms}?sort=${what}`)
}

App.do_sort = (what) => {
  if ((what === App.sort) || (what === `${App.sort}_desc`)) {
    if (App.sort === `${what}_desc`) {
      App.sort_action(what)
    }
    else {
      App.sort_action(what, true)
    }
  }
  else {
    App.sort_action(what)
  }
}

App.mod_user = (what, value, vtype) => {
  let items = App.get_selected()

  if (!items.length) {
    return
  }

  let s = App.singplural(`user`, items.length)
  let w = App.capitalize(what)

  let confirm_args = {
    message: `Modify ${items.length} ${s} (${w}) ?`,
    callback_yes: () => {
      App.msg_user_edit.close()
      App.do_mod_user(items, what, value, vtype)
    },
  }

  App.confirmbox(confirm_args)
}

App.do_mod_user = async (items, what, value, vtype) => {
  let ids = items.map(x => x.dataset.user_id)

  try {
    let response = await fetch(`/mod_user`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({ids, what, value, vtype}),
    })

    if (response.ok) {
      App.location(`/admin/users`)
    }
    else {
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
  }
}

App.delete_all = () => {
  if (App.mode === `admin_users`) {
    let confirm_args = {
      message: `Delete all non-admin users ?`,
      callback_yes: () => {
        App.delete_normal_users()
      },
    }

    App.confirmbox(confirm_args)
  }
  else if (App.mode === `admin_posts`) {
    let confirm_args = {
      message: `Delete ALL posts ?`,
      callback_yes: () => {
        App.delete_all_posts()
      },
    }

    App.confirmbox(confirm_args)
  }
  else if (App.mode === `admin_reactions`) {
    let confirm_args = {
      message: `Delete ALL reactions ?`,
      callback_yes: () => {
        App.delete_all_reactions()
      },
    }

    App.confirmbox(confirm_args)
  }
}

App.do_filter = () => {
  function clean(s) {
    s = s.toLowerCase()
    return s.replace(/[\s:]/g, ``).trim()
  }

  let filter = DOM.el(`#filter`)
  let items = DOM.els(`.item`)
  let value = clean(filter.value.toLowerCase())

  for (let item of items) {
    let name = item.dataset.name
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
    let list = item.dataset.reader
    let value_ = item.dataset.value
    let num_posts = item.dataset.num_posts
    let num_reactions = item.dataset.num_reactions
    let show = item.dataset.show

    let opts = [
      name, ago, date, size, title, original, uploader, views,
      listed, mtype, uname, ext, username, rpm, max_size, mark, show,
      reg_date, last_date, admin, list, value_, num_posts, num_reactions,
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
    return
  }

  let size = 0

  for (let reaction of App.selected_items) {
    size += parseFloat(reaction.dataset.size)
  }

  let s = App.singplural(`reaction`, App.selected_items.length)

  let confirm_args = {
    message: `Delete ${App.selected_items.length} ${s} ?`,
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
  try {
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
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
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
  try {
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
      App.print_error(response.status)
    }
  }
  catch (error) {
    App.print_error(error)
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
    App.msg_user_edit = Msg.factory()
    let t = DOM.el(`#template_user_edit`)
    App.msg_user_edit.set(t.innerHTML)

    DOM.ev(`#edit_reader_yes`, `click`, () => {
      App.mod_user(`reader`, 1, `bool`)
    })

    DOM.ev(`#edit_reader_no`, `click`, () => {
      App.mod_user(`reader`, 0, `bool`)
    })

    DOM.ev(`#edit_lister_yes`, `click`, () => {
      App.mod_user(`lister`, 1, `bool`)
    })

    DOM.ev(`#edit_lister_no`, `click`, () => {
      App.mod_user(`lister`, 0, `bool`)
    })

    DOM.ev(`#edit_reacter_yes`, `click`, () => {
      App.mod_user(`reacter`, 1, `bool`)
    })

    DOM.ev(`#edit_reacter_no`, `click`, () => {
      App.mod_user(`reacter`, 0, `bool`)
    })

    DOM.ev(`#edit_admin_yes`, `click`, () => {
      App.mod_user(`admin`, 1, `bool`)
    })

    DOM.ev(`#edit_admin_no`, `click`, () => {
      App.mod_user(`admin`, 0, `bool`)
    })

    DOM.ev(`#edit_rpm`, `click`, () => {
      App.user_mod_input(`rpm`, `number`)
    })

    DOM.ev(`#edit_max_size`, `click`, () => {
      App.user_mod_input(`max_size`, `number`)
    })

    DOM.ev(`#edit_mark`, `click`, () => {
      App.user_mod_input(`mark`, `string`)
    })

    DOM.ev(`#edit_name`, `click`, () => {
      App.user_mod_input(`name`, `string`)
    })

    DOM.ev(`#edit_username`, `click`, () => {
      App.user_mod_input(`username`, `string`)
    })

    DOM.ev(`#edit_password`, `click`, () => {
      App.user_mod_input(`password`, `password`)
    })

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
    App.msg_post_edit = Msg.factory()
    let t = DOM.el(`#template_post_edit`)
    App.msg_post_edit.set(t.innerHTML)

    DOM.ev(DOM.el(`#edit_title`), `click`, () => {
      let item = App.get_selected()[0]
      App.edit_post_title(item)
    })

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
    if (App.filter_focused()) {
      if (e.key === `Enter`) {
        App.do_search()
      }
      else if (e.key === `Escape`) {
        if (filter.value) {
          filter.value = ``
          App.do_filter()
        }
        else {
          filter.blur()
        }
      }
    }
  })
}

App.click_events = () => {
  DOM.ev(document, `click`, async (e) => {
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
      App.do_search(mtype)
    }
    else {
      let header = e.target.closest(`.header_text`)

      if (header) {
        let sort = e.target.dataset.sort

        if (sort) {
          App.do_sort(sort)
        }
      }
    }
  })
}

App.setup_pages = () => {
  let prev_page = DOM.el(`#prev_page`)

  if (prev_page) {
    DOM.ev(prev_page, `click`, () => {
      if (App.page <= 1) {
        return
      }

      App.goto_page(App.page - 1)
    })
  }

  let next_page = DOM.el(`#next_page`)

  if (next_page) {
    DOM.ev(next_page, `click`, () => {
      if (!App.next_page) {
        return
      }

      App.goto_page(App.page + 1)
    })
  }
}

App.refresh = () => {
  let ms = App.mode_string()
  App.location(`/${ms}`)
}