let selected_files = []
let date_mode = `ago`

window.onload = () => {
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
        let size = item.dataset.size_str.toLowerCase()
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