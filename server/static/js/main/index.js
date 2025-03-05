window.onload = () => {
  let image = DOM.el(`#image`)
  vars.num_pickers = 0
  vars.clicked = false

  if (image) {
    DOM.ev(image, `click`, (e) => {
      if (!vars.is_user) {
        popmsg(`Login or register first`)
        return
      }

      file_trigger()
    })
  }

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = get_empty_picker()
      let dataTransfer = new DataTransfer()
      dataTransfer.items.add(files[0])
      file.files = dataTransfer.files
      reflect_file(file)
    }
  })

  let video = DOM.el(`#video`)

  if (video) {
    DOM.ev(video, `loadeddata`, () => {
      video.muted = true
      video.play()
    })
  }

  let menu_btn = DOM.el(`#menu_btn`)

  if (menu_btn) {
    setup_explore_opts(false)

    DOM.ev(menu_btn, `click`, (e) => {
      vars.msg_explore_opts.show()
    })

    DOM.ev(menu_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        window.location = `/fresh`
      }
    })
  }

  let login_btn = DOM.el(`#login_btn`)

  if (login_btn) {
    DOM.ev(login_btn, `click`, (e) => {
      window.location = `/login`
    })
  }

  let register_btn = DOM.el(`#register_btn`)

  if (register_btn) {
    DOM.ev(register_btn, `click`, (e) => {
      window.location = `/register`
    })
  }

  let submit_btn = DOM.el(`#submit_btn`)

  if (submit_btn) {
    DOM.ev(submit_btn, `click`, (e) => {
      if (validate()) {
        let form = DOM.el(`#form`)
        form.submit()
      }
    })

    DOM.ev(submit_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        remove_last_picker()
      }
    })
  }

  let zip = DOM.el(`#zip`)

  if (zip) {
    DOM.ev(zip, `click`, (e) => {
      if (e.target.id === `compress`) {
        return
      }

      DOM.el(`#compress`).click()
    })
  }

  add_picker()

  let add_picker_btn = DOM.el(`#add_picker_btn`)

  if (add_picker_btn) {
    DOM.ev(add_picker_btn, `click`, (e) => {
      add_picker()
    })
  }

  let remove_picker_btn = DOM.el(`#remove_picker_btn`)

  if (remove_picker_btn) {
    DOM.ev(remove_picker_btn, `click`, (e) => {
      remove_picker()
    })
  }
}

function validate() {
  if (vars.clicked) {
    return false
  }

  let files = DOM.els(`.picker_file`)
  let ok_file = false

  for (let file of files) {
    let file_length = file.files.length

    if (file_length === 0) {
      continue
    }

    if (file_length > 1) {
      return false
    }

    if (file.files[0].size > vars.max_size) {
      return false
    }

    if (file.files[0].name) {
      ok_file = true
    }
  }

  if (!ok_file) {
    file_trigger()
    return false
  }

  let title = DOM.el(`#title`)

  if (title) {
    if (title.value.length > vars.max_title_length) {
      return false
    }
  }

  vars.clicked = true
  return true
}

function reflect_file(file) {
  let title = DOM.el(`#title`)

  if (title) {
    title.focus()
  }

  let the_file = file.files[0]

  if (the_file.size > vars.max_size) {
    reset_file(file)
    popmsg(`That file is too big`)
    return false
  }

  reset_image()
  video.pause()
  DOM.hide(video)

  if (is_image(the_file)) {
    let reader = new FileReader()

    reader.onload = (e) => {
      image.src = e.target.result
    }

    DOM.hide(video)
    DOM.show(image)
    reader.readAsDataURL(the_file)
  }
  else if (is_audio(the_file) || is_video(the_file)) {
    video.src = URL.createObjectURL(the_file)
    DOM.hide(image)
    DOM.show(video)
    video.load()
  }

  return true
}

function reset_file(file) {
  file.value = null
  reset_image()
  reset_video()
  DOM.show(`#image`)
}

function reset_image() {
  let image = DOM.el(`#image`)
  image.src = `/static/img/banners/${vars.banner}`
}

function reset_video() {
  let video = DOM.el(`#video`)
  video.pause()
  DOM.hide(video)
}

function add_picker(show = true) {
  if (vars.num_pickers > 0) {
    let empty = get_empty_picker()

    if (empty.files.length === 0) {
      empty.click()
      return
    }
  }

  vars.num_pickers += 1

  if (vars.num_pickers > vars.max_upload_files) {
    return
  }

  let t = DOM.el(`#template_picker`)
  let el = DOM.create(`div`, `picker`)
  el.innerHTML = t.innerHTML
  let input = DOM.el(`input`, el)
  input.id = `file_${vars.num_pickers}`
  input.name = `file`

  DOM.ev(el, `change`, (e) => {
    vars.clicked = false

    if (reflect_file(input)) {
      add_picker(false)
    }
  })

  DOM.ev(el, `click`, (e) => {
    if (e.shiftKey || e.ctrlKey || e.altKey) {
      e.preventDefault()
      reset_file(input)
    }
  })

  DOM.ev(el, `auxclick`, (e) => {
    if (e.button === 1) {
      e.preventDefault()

      if (vars.num_pickers > 1) {
        el.remove()
        vars.num_pickers -= 1
      }
      else {
        reset_file(input)
      }
    }
  })

  let c = DOM.el(`#pickers`)
  c.appendChild(el)
  check_compress()

  if (show) {
    input.click()
  }
}

function remove_picker() {
  if (vars.num_pickers <= 1) {
    return
  }

  let c = DOM.el(`#pickers`)
  c.removeChild(c.lastChild)
  vars.num_pickers -= 1
  check_compress()
}

function check_compress() {
  let checkbox = DOM.el(`#compress`)

  if (!checkbox) {
    return
  }

  if (vars.num_pickers > 1) {
    checkbox.checked = true
    checkbox.disabled = true
  }
  else {
    checkbox.checked = false
    checkbox.disabled = false
  }
}

function file_trigger() {
  let file = get_empty_picker()

  if (file) {
    file.click()
  }
}

function get_empty_picker() {
  let files = DOM.els(`.picker_file`)

  for (let file of files) {
    if (file.files.length === 0) {
      return file
    }
  }

  return files[0]
}

function remove_last_picker() {
  let pickers = DOM.els(`.picker_file`)

  if (!pickers.length) {
    return
  }

  if (pickers.length === 1) {
    reset_file(pickers[0])
    return
  }

  pickers.at(-1).parentNode.remove()
}