window.onload = () => {
  vars.selected_items = []
  vars.last_checkbox = null

  DOM.ev(document, `keyup`, (e) => {
    if (!filter_focused() && !Msg.msg.any_open()){
      if (e.key === `Escape`) {
        show_menu()
      }
    }
  })

  DOM.ev(document, `keydown`, (e) => {
    if (filter_focused()) {
      if (e.key === `Enter`) {
        do_search()
      }
      else if (e.key === `Escape`) {
        if (filter.value) {
          filter.value = ``
          do_filter()
        }
        else {
          filter.blur()
        }
      }
    }
  })

  DOM.ev(document, `click`, async (e) => {
    let item = e.target.closest(`.item`)
    vars.active_item = item

    if (e.target.classList.contains(`select_checkbox`)) {
      on_checkbox_click(e)
    }
    else if (e.target.classList.contains(`admin_user`)) {
      vars.user_opts_user_id = item.dataset.user_id
      vars.msg_user_opts.show()
    }
    else if (e.target.classList.contains(`mtype`)) {
      let mtype = e.target.textContent
      do_search(mtype)
    }
    else {
      let header = e.target.closest(`.header_text`)

      if (header) {
        let sort = e.target.dataset.sort

        if (sort) {
          do_sort(sort)
        }
      }
    }
  })

  let refresh = DOM.el(`#refresh`)

  if (refresh) {
    let ms = mode_string()

    DOM.ev(refresh, `click`, () => {
      window.location = `/${ms}`
    })
  }

  let del_sel = DOM.el(`#delete_selected`)

  if (del_sel) {
    DOM.ev(del_sel, `click`, () => {
      delete_selected()
    })
  }

  let edit = DOM.el(`#edit`)

  if (edit) {
    vars.msg_user_edit = Msg.factory()
    let t = DOM.el(`#template_user_edit`)
    vars.msg_user_edit.set(t.innerHTML)

    if (vars.mode === `admin_users`) {
      DOM.ev(`#edit_reader_yes`, `click`, () => {
        mod_user(`reader`, 1, `bool`)
      })

      DOM.ev(`#edit_reader_no`, `click`, () => {
        mod_user(`reader`, 0, `bool`)
      })

      DOM.ev(`#edit_lister_yes`, `click`, () => {
        mod_user(`lister`, 1, `bool`)
      })

      DOM.ev(`#edit_lister_no`, `click`, () => {
        mod_user(`lister`, 0, `bool`)
      })

      DOM.ev(`#edit_reacter_yes`, `click`, () => {
        mod_user(`reacter`, 1, `bool`)
      })

      DOM.ev(`#edit_reacter_no`, `click`, () => {
        mod_user(`reacter`, 0, `bool`)
      })

      DOM.ev(`#edit_admin_yes`, `click`, () => {
        mod_user(`admin`, 1, `bool`)
      })

      DOM.ev(`#edit_admin_no`, `click`, () => {
        mod_user(`admin`, 0, `bool`)
      })

      DOM.ev(`#edit_rpm`, `click`, () => {
        user_mod_input(`rpm`, `number`)
      })

      DOM.ev(`#edit_max_size`, `click`, () => {
        user_mod_input(`max_size`, `number`)
      })

      DOM.ev(`#edit_mark`, `click`, () => {
        user_mod_input(`mark`, `string`)
      })

      DOM.ev(`#edit_name`, `click`, () => {
        user_mod_input(`name`, `string`)
      })

      DOM.ev(`#edit_username`, `click`, () => {
        user_mod_input(`username`, `string`)
      })

      DOM.ev(`#edit_password`, `click`, () => {
        user_mod_input(`password`, `password`)
      })
    }

    DOM.ev(edit, `click`, () => {
      if (get_selected().length > 0) {
        vars.msg_user_edit.show()
      }
      else {
        popmsg(`No users are selected`)
      }
    })
  }

  let page_select = DOM.el(`#page_select`)

  if (page_select) {
    fill_page_select(page_select)

    DOM.ev(page_select, `change`, () => {
      on_page_select_change(page_select)
    })
  }

  let filter = DOM.el(`#filter`)

  if (filter) {
    DOM.ev(filter, `input`, () => {
      do_filter()
    })

    filter.focus()
  }

  let cb = DOM.el(`#checkbox`)

  if (cb) {
    DOM.ev(cb, `click`, () => {
      toggle_select()
    })
  }

  let add = DOM.el(`#add`)

  if (add) {
    DOM.ev(add, `click`, () => {
      window.location = `/edit_user`
    })
  }

  let prev_page = DOM.el(`#prev_page`)

  if (prev_page) {
    DOM.ev(prev_page, `click`, () => {
      if (vars.page <= 1) {
        return
      }

      goto_page(vars.page - 1)
    })
  }

  let next_page = DOM.el(`#next_page`)

  if (next_page) {
    DOM.ev(next_page, `click`, () => {
      if (!vars.next_page) {
        return
      }

      goto_page(vars.page + 1)
    })
  }

  let del_all = DOM.el(`#delete_all`)

  if (del_all) {
    DOM.ev(del_all, `click`, () => {
      delete_all()
    })
  }

  let explore_opts = DOM.el(`#template_explore_opts`)

  if (explore_opts) {
    setup_explore_opts()

    let menu = DOM.el(`#menu`)

    if (menu) {
      DOM.ev(menu, `click`, (e) => {
        show_menu()
      })
    }
  }

  let user_opts = DOM.el(`#template_user_opts`)

  if (user_opts) {
    setup_user_opts()
  }

  for (let el of DOM.els(`.reaction_value`)) {
    let v = el.innerText
    el.innerHTML = text_html(v, false)
  }

  for (let el of DOM.els(`.last_reaction`)) {
    let v = el.innerText
    el.innerHTML = text_html(v, false)
  }

  let clear_filter_btn = DOM.el(`#clear_filter`)

  if (clear_filter_btn) {
    DOM.ev(clear_filter_btn, `click`, () => {
      clear_filter()
    })
  }
}

function goto_page(page) {
  let psize = vars.page_size
  let url = new URL(window.location.href)
  url.searchParams.set(`page`, page)
  url.searchParams.set(`page_size`, psize)

  if (vars.used_user_id) {
    url.searchParams.set(`user_id`, vars.used_user_id)
  }

  window.location.href = url.href
}

function fill_page_select(page_select) {
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

  add_option(`Default`, vars.def_page_size)
  add_separator()

  let nums = [5, 10, 20, 50, 100, 200, 500, 1000]

  for (let n of nums) {
    let selected = false

    if (!vars.def_page_size) {
      if (vars.page_size === n.toString()) {
        selected = true
      }
    }

    add_option(n, selected)
  }

  add_separator()
  add_option(`All`, vars.page_size === `all`)
}

function on_page_select_change(page_select) {
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

function delete_posts() {
  if (vars.selected_items.length === 0) {
    return
  }

  let size = 0

  for (let post of vars.selected_items) {
    size += parseFloat(post.dataset.size)
  }

  size = Math.round(size * 100) / 100
  let s = singplural(`post`, vars.selected_items.length)

  let confirm_args = {
    message: `Delete ${vars.selected_items.length} ${s} (${size_string(size)}) ?`,
    callback_yes: () => {
      let posts = []

      for (let post of vars.selected_items) {
        posts.push(post.dataset.post_id)
      }

      delete_selected_posts(posts)
    },
  }

  confirmbox(confirm_args)
}

async function delete_selected_posts(ids) {
  try {
    let response = await fetch(`/delete_posts`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({ids}),
    })

    if (response.ok) {
      remove_posts(ids)
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function remove_posts(posts) {
  for (let post of posts) {
    let el = DOM.el(`.item[data-post_id="${post}"]`)

    if (el) {
      el.remove()
    }
  }
}

async function delete_all_posts() {
  try {
    let response = await fetch(`/delete_all_posts`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify(),
    })

    if (response.ok) {
      window.location = `/admin/posts`
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function select_all() {
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    checkbox.checked = true
  }

  DOM.el(`#checkbox`).checked = true
}

function unselect_all() {
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    checkbox.checked = false
  }

  DOM.el(`#checkbox`).checked = false
}

function size_string(size) {
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

function do_search(query = ``) {
  if (!query) {
    query = DOM.el(`#filter`).value.trim()
  }

  if (!query) {
    return
  }

  let ms = mode_string()

  if (query) {
    window.location = `/${ms}?query=${encode_uri(query)}`
  }
  else {
    window.location = `/${ms}`
  }
}

async function edit_post_title(el) {
  let t = el.dataset.title
  let o = el.dataset.original
  let current = t || o

  let prompt_args = {
    placeholder: `Enter new title`,
    value: current,
    max: vars.max_title_length,
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
        print_error(response.status)
      }
    },
  }

  prompt_text(prompt_args)
}

function toggle_select() {
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    if (!checkbox.checked) {
      select_all()
      return
    }
  }

  unselect_all()
}

function get_selected() {
  let items = []
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    if (checkbox.checked) {
      items.push(checkbox.closest(`.item`))
    }
  }

  return items
}

function delete_selected() {
  let items = get_selected()

  if (items.length === 0) {
    return
  }

  vars.selected_items = items

  if (vars.mode === `admin_users`) {
    delete_users()
  }
  else if (vars.mode === `admin_posts`) {
    delete_posts()
  }
  else if (vars.mode === `admin_reactions`) {
    delete_reactions()
  }
}

function delete_users() {
  if (vars.selected_items.length === 0) {
    return
  }

  let size = 0

  for (let user of vars.selected_items) {
    size += parseFloat(user.dataset.size)
  }

  size = Math.round(size * 100) / 100
  let s = singplural(`user`, vars.selected_items.length)

  let confirm_args = {
    message: `Delete ${vars.selected_items.length} ${s} ?`,
    callback_yes: () => {
      let users = []

      for (let user of vars.selected_items) {
        users.push(user.dataset.user_id)
      }

      delete_selected_users(users)
    },
  }

  confirmbox(confirm_args)
}

async function delete_selected_users(ids) {
  try {
    let response = await fetch(`/delete_users`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({ids}),
    })

    if (response.ok) {
      remove_users(ids)
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function remove_users(ids) {
  for (let id of ids) {
    let el = DOM.el(`.item[data-user_id="${id}"]`)

    if (el) {
      el.remove()
    }
  }
}

async function delete_normal_users() {
  try {
    let response = await fetch(`/delete_normal_users`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify(),
    })

    if (response.ok) {
      window.location = `/admin/users`
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function sort_action(what, desc = false) {
  if (desc) {
    what = what + `_desc`
  }

  let ms = mode_string()
  window.location = `/${ms}?sort=${what}`
}

function do_sort(what) {
  if ((what === vars.sort) || (what === `${vars.sort}_desc`)) {
    if (vars.sort === `${what}_desc`) {
      sort_action(what)
    }
    else {
      sort_action(what, true)
    }
  }
  else {
    sort_action(what)
  }
}

function mod_user(what, value, vtype) {
  let items = get_selected()

  if (!items.length) {
    return
  }

  let s = singplural(`user`, items.length)
  let w = capitalize(what)

  let confirm_args = {
    message: `Modify ${items.length} ${s} (${w}) ?`,
    callback_yes: () => {
      vars.msg_user_edit.close()
      do_mod_user(items, what, value, vtype)
    },
  }

  confirmbox(confirm_args)
}

async function do_mod_user(items, what, value, vtype) {
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
      window.location = `/admin/users`
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function delete_all() {
  if (vars.mode === `admin_users`) {
    let confirm_args = {
      message: `Delete all non-admin users ?`,
      callback_yes: () => {
        delete_normal_users()
      },
    }

    confirmbox(confirm_args)
  }
  else if (vars.mode === `admin_posts`) {
    let confirm_args = {
      message: `Delete ALL posts ?`,
      callback_yes: () => {
        delete_all_posts()
      },
    }

    confirmbox(confirm_args)
  }
  else if (vars.mode === `admin_reactions`) {
    let confirm_args = {
      message: `Delete ALL reactions ?`,
      callback_yes: () => {
        delete_all_reactions()
      },
    }

    confirmbox(confirm_args)
  }
}

function do_filter() {
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

function mode_string() {
  let split = vars.mode.split(`_`)
  return split.join(`/`)
}

function delete_reactions() {
  if (vars.selected_items.length === 0) {
    return
  }

  let size = 0

  for (let reaction of vars.selected_items) {
    size += parseFloat(reaction.dataset.size)
  }

  let s = singplural(`reaction`, vars.selected_items.length)

  let confirm_args = {
    message: `Delete ${vars.selected_items.length} ${s} ?`,
    callback_yes: () => {
      let reactions = []

      for (let reaction of vars.selected_items) {
        reactions.push(parseInt(reaction.dataset.id))
      }

      delete_selected_reactions(reactions)
    },
  }

  confirmbox(confirm_args)
}

async function delete_selected_reactions(ids) {
  try {
    let response = await fetch(`/delete_reactions`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({ids}),
    })

    if (response.ok) {
      remove_reactions(ids)
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function remove_reactions(reactions) {
  for (let id of reactions) {
    let el = DOM.el(`.item[data-id="${id}"]`)

    if (el) {
      el.remove()
    }
  }
}

async function delete_all_reactions() {
  try {
    let response = await fetch(`/delete_all_reactions`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify(),
    })

    if (response.ok) {
      window.location = `/admin/reactions`
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function show_menu() {
  vars.msg_explore_opts.show()
}

function filter_focused() {
  let filter = DOM.el(`#filter`)
  return filter && (document.activeElement === filter)
}

function on_checkbox_click(e) {
  if (e.shiftKey && vars.last_checkbox) {
    let checked = vars.last_checkbox.checked
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
      else if (box === vars.last_checkbox) {
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

  vars.last_checkbox = e.target
}

function set_filter(value) {
  let filter = DOM.el(`#filter`)
  filter.value = value
  do_filter()
}

function clear_filter() {
  set_filter(``)
}