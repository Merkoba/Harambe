window.onload = () => {
  vars.selected_items = []

  DOM.ev(document, `keyup`, async (e) => {
    if (e.key === `Enter`) {
      do_search()
    }
  })

  DOM.ev(document, `click`, async (e) => {
    let item = e.target.closest(`.item`)

    if (e.target.classList.contains(`edit`)) {
      if (vars.mode === `users`) {
        window.location = `/edit_user/${item.dataset.username}`
      }
      else if (vars.mode === `posts`) {
        edit_title(item)
      }
    }

    if (e.target.classList.contains(`delete`)) {
      vars.selected_items = [e.target.closest(`.item`)]

      if (vars.mode === `users`) {
        delete_users()
      }
      else if (vars.mode === `posts`) {
        delete_posts()
      }
      else if (vars.mode === `reactions`) {
        delete_reactions()
      }
    }

    if (e.target.classList.contains(`delete_above`)) {
      select_above(item)
    }

    if (e.target.classList.contains(`delete_below`)) {
      select_below(item)
    }

    let header = e.target.closest(`.table_header`)

    if (header) {
      let sort = e.target.dataset.sort

      if (sort) {
        do_sort(sort)
      }
    }
  })

  DOM.ev(document, `auxclick`, async (e) => {
    if (e.button !== 1) {
      return
    }

    let item = e.target.closest(`.item`)

    if (e.target.classList.contains(`edit`)) {
      if (vars.mode === `users`) {
        window.open(`/edit_user/${item.dataset.username}`, `_blank`)
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
    vars.msg_edit = Msg.factory()
    let t = DOM.el(`#template_edit`)
    vars.msg_edit.set(t.innerHTML)

    if (vars.mode === `users`) {
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
    }

    DOM.ev(edit, `click`, () => {
      if (get_selected().length > 0) {
        vars.msg_edit.show()
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
}

function goto_page(page) {
  let psize = vars.page_size
  let url = new URL(window.location.href)
  url.searchParams.set(`page`, page)
  url.searchParams.set(`page_size`, psize)

  if (vars.username) {
    url.searchParams.set(`username`, vars.username)
  }

  window.location.href = url.href
}

function select_above(el) {
  let items = DOM.els(`.item`)
  let changed = false
  let start = true

  for (let item of items) {
    let cb = DOM.el(`.select_checkbox`, item)

    if (start) {
      if (!cb.checked) {
        cb.checked = true
        changed = true
      }
    }
    else if (cb.checked) {
      cb.checked = false
      changed = true
    }

    if (item === el) {
      start = false
    }
  }

  if (!changed) {
    unselect_all()
  }
}

function select_below(el) {
  let items = DOM.els(`.item`)
  let start = false
  let changed = false

  for (let item of items) {
    let cb = DOM.el(`.select_checkbox`, item)

    if (item === el) {
      start = true
    }

    if (start) {
      if (!cb.checked) {
        cb.checked = true
        changed = true
      }
    }
    else if (cb.checked) {
      cb.checked = false
      changed = true
    }
  }

  if (!changed) {
    unselect_all()
  }
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

  if (confirm(`Delete ${vars.selected_items.length} ${s} (${size_string(size)}) ?`)) {
    let posts = []

    for (let post of vars.selected_items) {
      posts.push(post.dataset.name)
    }

    delete_selected_posts(posts)
  }
}

async function delete_selected_posts(names) {
  try {
    let response = await fetch(`/delete_posts`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({names}),
    })

    if (response.ok) {
      remove_posts(names)
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
    let el = DOM.el(`.item[data-name="${post}"]`)

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

function do_search() {
  let query = DOM.el(`#filter`).value.trim()

  if (!query) {
    return
  }

  let ms = mode_string()

  if (query) {
    window.location = `/${ms}?query=${query}`
  }
  else {
    window.location = `/${ms}`
  }
}

async function edit_title(el) {
  let t = el.dataset.title
  let o = el.dataset.original

  prompt_text(`New title`, t || o, async (title) => {
    let name = el.dataset.name

    let response = await fetch(`/edit_title`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({name, title}),
    })

    if (response.ok) {
      el.dataset.title = title
      DOM.el(`.title`, el).innerText = title || o
    }
    else {
      print_error(response.status)
    }
  })
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

  if (vars.mode === `users`) {
    delete_users()
  }
  else if (vars.mode === `posts`) {
    delete_posts()
  }
  else if (vars.mode === `reactions`) {
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

  if (confirm(`Delete ${vars.selected_items.length} ${s} ?`)) {
    let users = []

    for (let user of vars.selected_items) {
      users.push(user.dataset.username)
    }

    delete_selected_users(users)
  }
}

async function delete_selected_users(usernames) {
  try {
    let response = await fetch(`/delete_users`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({usernames}),
    })

    if (response.ok) {
      remove_users(usernames)
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function remove_users(usernames) {
  for (let username of usernames) {
    let el = DOM.el(`.item[data-username="${username}"]`)

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
  if (what === vars.sort) {
    sort_action(what, true)
  }
  else if (vars.sort.includes(`_desc`)) {
    sort_action(what)
  }
  else {
    sort_action(what, true)
  }
}

function mod_user(what, value, vtype) {
  let items = get_selected()

  if (!items.length) {
    return
  }

  let s = singplural(`user`, items.length)
  let v = value === 1 ? `Yes` : `No`
  let w = capitalize(what)

  if (confirm(`Modify ${items.length} ${s} (${w}: ${v}) ?`)) {
    vars.msg_edit.close()
    do_mod_user(items, what, value, vtype)
  }
}

async function do_mod_user(items, what, value, vtype) {
  let usernames = items.map(x => x.dataset.username)

  try {
    let response = await fetch(`/mod_user`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({usernames, what, value, vtype}),
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
  if (vars.mode === `users`) {
    if (confirm(`Delete all non-admin users ?`)) {
      if (confirm(`Are you really sure ?`)) {
        delete_normal_users()
      }
    }
  }
  else if (vars.mode === `posts`) {
    if (confirm(`Delete ALL posts ?`)) {
      if (confirm(`Are you really sure ?`)) {
        delete_all_posts()
      }
    }
  }
  else if (vars.mode === `reactions`) {
    if (confirm(`Delete ALL reactions ?`)) {
      if (confirm(`Are you really sure ?`)) {
        delete_all_reactions()
      }
    }
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
    let opts = []

    if (vars.mode === `users`) {
      let username = item.dataset.username
      let name = item.dataset.name
      let rpm = item.dataset.rpm
      let max_size = item.dataset.max_size
      let mark = item.dataset.mark
      let reg_date = item.dataset.reg_date
      let last_date = item.dataset.last_date
      let admin = item.dataset.admin
      let list = item.dataset.reader

      opts = [
        username, name, rpm, max_size,
        mark, reg_date, last_date, admin, list,
      ]
    }
    else if ((vars.mode === `posts`) || (vars.mode === `list`)) {
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

      opts = [
        name, size, title, original, ago, date,
        uploader, views, listed, mtype, uname, ext,
      ]
    }

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
  if (vars.mode === `list`) {
    return `list`
  }

  return `admin/${vars.mode}`
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

  if (confirm(`Delete ${vars.selected_items.length} ${s} ?`)) {
    let reactions = []

    for (let reaction of vars.selected_items) {
      reactions.push(parseInt(reaction.dataset.id))
    }

    delete_selected_reactions(reactions)
  }
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