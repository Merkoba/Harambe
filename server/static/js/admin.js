let selected_files = []
let selected_users = []
let date_mode = `ago`

window.onload = () => {
  DOM.ev(document, `keyup`, async (e) => {
    if (vars.mode === `admin`) {
      if (e.key === `Enter`) {
        do_search()
      }
    }
  })

  DOM.ev(document, `click`, async (e) => {
    let item = e.target.closest(`.item`)

    if (e.target.classList.contains(`edit`)) {
      if (vars.mode === `users`) {
        window.location = `/edit_user/${item.dataset.username}`
      }
      else {
        edit_title(item)
      }
    }

    if (e.target.classList.contains(`delete`)) {
      if (vars.mode === `users`) {
        selected_users = [e.target.closest(`.item`)]
        delete_users()
      }
      else {
        selected_files = [e.target.closest(`.item`)]
        delete_files()
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

  let refresh = DOM.el(`#refresh`)

  if (refresh) {
    DOM.ev(refresh, `click`, () => {
      window.location = `/${vars.mode}`
    })
  }

  let del_sel = DOM.el(`#delete_selected`)

  if (del_sel) {
    DOM.ev(del_sel, `click`, () => {
      delete_selected()
    })
  }

  let delete_all = DOM.el(`#delete_all`)

  if (delete_all) {
    DOM.ev(delete_all, `click`, () => {
      if (vars.mode === `users`) {
        if (confirm(`Delete all non-admin users?`)) {
            delete_normal_users()
        }
      }
      else {
        if (confirm(`Delete ALL files?`)) {
          delete_all_files()
        }
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
      let items = DOM.els(`.item`)
      let value = filter.value.toLowerCase()

      for (let item of items) {
        let opts = []

        if (vars.mode === `users`) {
          let username = item.dataset.username.toLowerCase()
          let name = item.dataset.name.toLowerCase()
          let rpm = item.dataset.rpm.toLowerCase()
          let max_size = item.dataset.max_size.toLowerCase()
          let mark = item.dataset.mark.toLowerCase()
          let reg_date = item.dataset.reg_date.toLowerCase()
          let last_date = item.dataset.last_date.toLowerCase()
          let admin = item.dataset.admin.toLowerCase()
          let list = item.dataset.can_list.toLowerCase()
          opts = [username, name, rpm, max_size, mark, reg_date, last_date, admin, list]
        }
        else {
          let name = item.dataset.name.toLowerCase()
          let ago = item.dataset.ago.toLowerCase()
          let date = item.dataset.date.toLowerCase()
          let size = item.dataset.size_str.toLowerCase()
          let title = item.dataset.title.toLowerCase()
          let original = item.dataset.original.toLowerCase()
          let uploader = item.dataset.uploader.toLowerCase()
          opts = [name, size, title, original, ago, date, uploader]
        }

        if (opts.some(x => x.includes(value))) {
          item.style.display = `flex`
        }
        else {
          item.style.display = `none`
        }
      }
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

  let can_list = DOM.el(`#can_list`)

  if (can_list) {
    DOM.ev(can_list, `click`, () => {
      can_list_selected()
    })
  }

  let no_list = DOM.el(`#no_list`)

  if (no_list) {
    DOM.ev(no_list, `click`, () => {
      no_list_selected()
    })
  }
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

  let nums = [10, 20, 50, 100, 200, 500, 1000]

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

function delete_files() {
  if (selected_files.length === 0) {
    return
  }

  let size = 0

  for (let file of selected_files) {
    size += parseFloat(file.dataset.size)
  }

  size = Math.round(size * 100) / 100

  if (confirm(`Delete (${selected_files.length} files) (${size_string(size)})`)) {
    let files = []

    for (let file of selected_files) {
      files.push(file.dataset.full)
    }

    delete_selected_files(files)
  }
}

async function delete_selected_files(files) {
  try {
    let response = await fetch(`/delete_files`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify({files}),
    })

    if (response.ok) {
      remove_files(files)
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function remove_files(files) {
  for (let file of files) {
    let el = DOM.el(`.item[data-full="${file}"]`)

    if (el) {
      el.remove()
    }
  }
}

async function delete_all_files() {
  try {
    let response = await fetch(`/delete_all_files`, {
      method: `POST`,
      headers: {
        "Content-Type": `application/json`,
      },
      body: JSON.stringify(),
    })

    if (response.ok) {
      window.location = `/admin`
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

function print_error(msg) {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
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

  if (query) {
    window.location = `/${vars.mode}?query=${query}`
  }
  else {
    window.location = `/${vars.mode}`
  }
}

async function edit_title(el) {
  let t = el.dataset.title
  let o = el.dataset.original
  let title = prompt(`New title`, t || o).trim()
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
  let checkboxes = DOM.els(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    if (checkbox.checked) {
      items.push(checkbox.closest(`.item`))
    }
  }
}

function delete_selected() {
  let items = get_selected()

  if (items.length === 0) {
    return
  }

  if (vars.mode === `users`) {
    selected_users = items
    delete_users()
  }
  else{
    selected_files = items
    delete_files()
  }
}

function delete_users() {
  if (selected_users.length === 0) {
    return
  }

  let size = 0

  for (let user of selected_users) {
    size += parseFloat(user.dataset.size)
  }

  size = Math.round(size * 100) / 100

  if (confirm(`Delete (${selected_users.length} users)`)) {
    let users = []

    for (let user of selected_users) {
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
      window.location = `/users`
    }
    else {
      print_error(response.status)
    }
  }
  catch (error) {
    print_error(error)
  }
}

function do_sort(what) {
  let url = new URL(window.location.href)
  let sort = url.searchParams.get(`sort`)

  if (sort) {
    if (sort === what) {
      window.location = `/${vars.mode}?sort=${what}_desc`
      return
    }
    else if (sort === `${what}_desc`) {
      window.location = `/${vars.mode}`
      return
    }
  }

  window.location = `/${vars.mode}?sort=${what}`
}

function list_selected() {
    try {
      let response = await fetch(`/list_yes`, {
        method: `POST`,
        headers: {
          "Content-Type": `application/json`,
        },
        body: JSON.stringify({files}),
      })

      if (response.ok) {
        remove_files(files)
      }
      else {
        print_error(response.status)
      }
    }
    catch (error) {
      print_error(error)
    }
}