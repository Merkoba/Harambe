let selected_files = []
let date_mode = `ago`

window.onload = () => {
  document.addEventListener(`click`, async (e) => {
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

  let s_all = document.querySelector(`#select_all`)

  if (s_all) {
    s_all.addEventListener(`click`, () => {
      select_all()
    })
  }

  let u_all = document.querySelector(`#unselect_all`)

  if (u_all) {
    u_all.addEventListener(`click`, () => {
      unselect_all()
    })
  }

  let delete_selected = document.querySelector(`#delete_selected`)

  if (delete_selected) {
    delete_selected.addEventListener(`click`, () => {
      let files = []
      let checkboxes = document.querySelectorAll(`.select_checkbox`)

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

  let delete_all = document.querySelector(`#delete_all`)

  if (delete_all) {
    delete_all.addEventListener(`click`, () => {
      if (confirm(`Delete All`)) {
        delete_all_files()
      }
    })
  }

  let page_select = document.querySelector(`#page_select`)

  if (page_select) {
    fill_page_select(page_select)

    page_select.addEventListener(`change`, () => {
      on_page_select_change(page_select)
    })
  }

  let filter = document.querySelector(`#filter`)

  if (filter) {
    filter.addEventListener(`input`, () => {
      let items = document.querySelectorAll(`.item`)
      let value = filter.value.toLowerCase()

      for (let item of items) {
        let name = item.dataset.name.toLowerCase()
        let ago = item.dataset.ago.toLowerCase()
        let date = item.dataset.date.toLowerCase()
        let size = item.dataset.size.toLowerCase()
        let opts = [name, size]

        if (date_mode === `ago`) {
          opts.push(ago)
        }
        else if (date_mode === `date`) {
          opts.push(date)
        }

        if (opts.some(x => x.includes(value))) {
          item.style.display = `flex`
        }
        else {
          item.style.display = `none`
        }
      }
    })
  }

  let age = document.querySelector(`#age`)

  if (age) {
    age.addEventListener(`click`, () => {
      if (date_mode === `ago`) {
        date_mode = `date`
      }
      else {
        date_mode = `ago`
      }

      for (let item of document.querySelectorAll(`.item`)) {
        if (date_mode === `ago`) {
          item.querySelector(`.date`).innerText = item.dataset.ago
        }
        else {
          item.querySelector(`.date`).innerText = item.dataset.date
        }
      }
    })
  }
}

function select_above(el) {
  let items = document.querySelectorAll(`.item`)
  let changed = false
  let start = true

  for (let item of items) {
    let cb = item.querySelector(`.select_checkbox`)

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
  let items = document.querySelectorAll(`.item`)
  let start = false
  let changed = false

  for (let item of items) {
    let cb = item.querySelector(`.select_checkbox`)

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

  add_option(`Default`, def_page_size)
  add_separator()

  let nums = [10, 20, 50, 100, 200, 500, 1000]

  for (let n of nums) {
    let selected = false

    if (!def_page_size) {
      if (page_size === n.toString()) {
        selected = true
      }
    }

    add_option(n, selected)
  }

  add_separator()
  add_option(`All`, page_size === `all`)
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
      files.push(file.dataset.name)
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
    let el = document.querySelector(`.item[data-name="${file}"]`)

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
      document.querySelector(`#items`).innerHTML = ``
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
  let checkboxes = document.querySelectorAll(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    checkbox.checked = true
  }
}

function unselect_all() {
  let checkboxes = document.querySelectorAll(`.select_checkbox`)

  for (let checkbox of checkboxes) {
    checkbox.checked = false
  }
}

function print_error(msg) {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
}

function size_string(size) {
  size /= 1000

  if (size < 1024) {
    return `${size.toFixed(2)} kb`
  }

  size /= 1000

  if (size < 1024) {
    return `${size.toFixed(2)} mb`
  }

  size /= 1000
  return `${size.toFixed(2)} gb`
}