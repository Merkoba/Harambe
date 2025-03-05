let clicked = false

window.onload = () => {
  let image = DOM.el(`#image`)
  let file = DOM.el(`#file`)
  vars.num_pickers = 0

  if (image) {
    DOM.ev(image, `click`, (e) => {
      if (!vars.is_user) {
        popmsg(`Login or register first`)
        return
      }

      if (e.shiftKey || e.ctrlKey || e.altKey) {
        reset_file()
        return
      }

      if (file) {
        file.click()
      }
    })

    DOM.ev(image, `auxclick`, (e) => {
      if (e.button === 1) {
        e.preventDefault()
        reset_file()
      }
    })
  }

  if (file) {
    DOM.ev(file, `change`, (e) => {
      clicked = false
      reflect_file()
    })

    DOM.ev(file, `click`, (e) => {
      if (e.shiftKey || e.ctrlKey || e.altKey) {
        e.preventDefault()
        reset_file()
      }
    })

    DOM.ev(file, `auxclick`, (e) => {
      if (e.button === 1) {
        e.preventDefault()
        reset_file()
      }
    })
  }

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = DOM.el(`#file`)
      let dataTransfer = new DataTransfer()
      dataTransfer.items.add(files[0])
      file.files = dataTransfer.files
      reflect_file()
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
        reset_file()
      }
    })
  }

  let zip = DOM.el(`#zip`)

  if (zip && file) {
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
  if (clicked) {
    return false
  }

  let file = DOM.el(`#file`)
  let file_length = file.files.length

  if (file_length === 0) {
    file.click()
    return false
  }

  if (file_length > 1) {
    return false
  }

  if (file.files[0].size > vars.max_size) {
    return false
  }

  let title = DOM.el(`#title`)

  if (title) {
    if (title.value.length > vars.max_title_length) {
      return false
    }
  }

  clicked = true
  return true
}

function reflect_file() {
  let title = DOM.el(`#title`)

  if (title) {
    title.focus()
  }

  let file = DOM.el(`#file`)
  let the_file = file.files[0]

  if (the_file.size > vars.max_size) {
    reset_file()
    popmsg(`That file is too big`)
    return
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
}

function reset_file() {
  let file = DOM.el(`#file`)
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

function add_picker() {
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

  DOM.ev(el, `click`, (e) => {
    input.click()
  })

  let c = DOM.el(`#pickers`)
  c.appendChild(el)
  check_archive()
}

function remove_picker() {
  if (vars.num_pickers <= 1) {
    return
  }

  let c = DOM.el(`#pickers`)
  c.removeChild(c.lastChild)
  vars.num_pickers -= 1
  check_archive()
}

function check_archive() {
  let checkbox = DOM.el(`#compress`)

  if (vars.num_pickers > 1) {
    checkbox.checked = true
    checkbox.disabled = true
  }
  else {
    checkbox.checked = false
    checkbox.disabled = false
  }
}