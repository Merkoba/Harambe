let selected_files = []
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
    if (e.target.classList.contains(`edit`)) {
      let el = e.target.closest(`.item`)
      edit_title(el)
    }

    if (e.target.classList.contains(`delete`)) {
      selected_files = [e.target.closest(`.item`)]
      delete_files()
    }

    if (e.target.classList.contains(`delete_above`)) {
      let el = e.target.closest(`.item`)
      select_above(el)
    }

    if (e.target.classList.contains(`delete_below`)) {
      let el = e.target.closest(`.item`)
      select_below(el)
    }
  })

  let refresh = DOM.el(`#refresh`)

  if (refresh) {
    DOM.ev(refresh, `click`, () => {
      window.location = `/admin`
    })
  }

  let delete_selected = DOM.el(`#delete_selected`)

  if (delete_selected) {
    DOM.ev(delete_selected`click`, () => {
      let files = []
      let checkboxes = DOM.els(`.select_checkbox`)

      for (let checkbox of checkboxes) {
        if (checkbox.checked) {
          files.push(checkbox.closest(`.item`))
        }
      }

      if (files.length === 0) {
        return
      }

      selected_files = files
      delete_files()
    })
  }

  let delete_all = DOM.el(`#delete_all`)

  if (delete_all) {
    DOM.ev(delete_all, `click`, () => {
      if (confirm(`Delete ALL files from the server?`)) {
        delete_all_files()
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
        let name = item.dataset.name.toLowerCase()
        let ago = item.dataset.ago.toLowerCase()
        let date = item.dataset.date.toLowerCase()
        let size = item.dataset.size_str.toLowerCase()
        let title = item.dataset.title.toLowerCase()
        let original = item.dataset.original.toLowerCase()
        let uploader = item.dataset.uploader.toLowerCase()
        let opts = [name, size, title, original, ago, date, uploader]

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

  let date = DOM.el(`#date`)

  if (date) {
    DOM.ev(date, `click`, () => {
      if (vars.mode === `admin`) {
        sort_date()
      }
      else if (vars.mode === `list`) {
        change_date()
      }
    })
  }

  let size = DOM.el(`#size`)

  if (size) {
    if (vars.mode === `admin`) {
      DOM.ev(size, `click`, () => {
        sort_size()
      })
    }
  }

  let views = DOM.el(`#views`)

  if (views) {
    DOM.ev(views, `click`, () => {
      if (vars.mode === `admin`) {
        sort_views()
      }
    })
  }

  let title = DOM.el(`#title`)

  if (title) {
    DOM.ev(title, `click`, () => {
      if (vars.mode === `admin`) {
        sort_title()
      }
    })
  }

  let name = DOM.el(`#name`)

  if (name) {
    DOM.ev(name, `click`, () => {
      if (vars.mode === `admin`) {
        sort_name()
      }
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

async function delete_file(name, el) {
  let files = [name]

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
      DOM.el(`#items`).innerHTML = ``
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
    window.location = `/admin?query=${query}`
  }
  else {
    window.location = `/admin`
  }
}

function sort_size() {
  let url = new URL(window.location.href)
  let sort = url.searchParams.get(`sort`)

  if (sort) {
    if (sort === `size`) {
      window.location = `/admin?sort=size_desc`
      return
    }
    else if (sort === `size_desc`) {
      window.location = `/admin`
      return
    }
  }

  window.location = `/admin?sort=size`
}

function sort_date() {
  let url = new URL(window.location.href)
  let sort = url.searchParams.get(`sort`)

  if (sort) {
    if (sort === `date_desc`) {
      window.location = `/admin`
      return
    }
  }

  window.location = `/admin?sort=date_desc`
}

function change_date() {
  if (date_mode === `ago`) {
    date_mode = `date`
  }
  else {
    date_mode = `ago`
  }

  for (let item of DOM.els(`.item`)) {
    if (date_mode === `ago`) {
      DOM.el(`.date`, item).innerText = item.dataset.ago
    }
    else {
      DOM.el(`.date`, item).innerText = item.dataset.date
    }
  }
}

function sort_views() {
  let url = new URL(window.location.href)
  let sort = url.searchParams.get(`sort`)

  if (sort) {
    if (sort === `views`) {
      window.location = `/admin?sort=views_desc`
      return
    }
    else if (sort === `views_desc`) {
      window.location = `/admin`
      return
    }
  }

  window.location = `/admin?sort=views`
}

function sort_title() {
  let url = new URL(window.location.href)
  let sort = url.searchParams.get(`sort`)

  if (sort) {
    if (sort === `title`) {
      window.location = `/admin?sort=title_desc`
      return
    }
    else if (sort === `title_desc`) {
      window.location = `/admin`
      return
    }
  }

  window.location = `/admin?sort=title`
}

function sort_name() {
  let url = new URL(window.location.href)
  let sort = url.searchParams.get(`sort`)

  if (sort) {
    if (sort === `name`) {
      window.location = `/admin?sort=name_desc`
      return
    }
    else if (sort === `name_desc`) {
      window.location = `/admin`
      return
    }
  }

  window.location = `/admin?sort=name`
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