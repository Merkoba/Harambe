DOM.ev(document, `DOMContentLoaded`, () => {
  App.init()
})

App.init = () => {
  let image = DOM.el(`#image`)
  App.num_pickers = 0
  App.clicked = false

  if (image) {
    DOM.ev(image, `click`, (e) => {
      if (!App.is_user) {
        App.popmsg(`Login or register first`)
        return
      }

      App.file_trigger()
    })

    DOM.ev(image, `auxclick`, (e) => {
      App.reset_file()
    })

    DOM.ev(image, `error`, (e) => {
      App.reset_file()
    })
  }

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = App.get_empty_picker()
      let dataTransfer = new DataTransfer()
      dataTransfer.items.add(files[0])
      file.files = dataTransfer.files
      App.reflect_file(file)
      App.add_picker()
    }
  })

  let video = DOM.el(`#video`)

  if (video) {
    DOM.ev(video, `loadeddata`, () => {
      video.muted = true
      video.play()
    })

    DOM.ev(video, `auxclick`, (e) => {
      App.reset_file()
    })

    DOM.ev(video, `error`, (e) => {
      App.reset_file()
    })
  }

  let menu_btn = DOM.el(`#menu_btn`)

  if (menu_btn) {
    App.setup_menu_opts()

    DOM.ev(menu_btn, `click`, (e) => {
      App.msg_show(`menu`)
    })

    DOM.ev(menu_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.location(`/fresh`)
      }
    })
  }

  let login_btn = DOM.el(`#login_btn`)

  if (login_btn) {
    DOM.ev(login_btn, `click`, (e) => {
      App.location(`/login`)
    })
  }

  let register_btn = DOM.el(`#register_btn`)

  if (register_btn) {
    DOM.ev(register_btn, `click`, (e) => {
      App.location(`/register`)
    })
  }

  let submit_btn = DOM.el(`#submit_btn`)

  if (submit_btn) {
    DOM.ev(submit_btn, `click`, (e) => {
      if (App.validate()) {
        let form = DOM.el(`#form`)
        form.submit()
      }
    })

    DOM.ev(submit_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.remove_picker()
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

  App.setup_pickers()
}

App.validate = () => {
  if (App.clicked) {
    return false
  }

  if (App.num_active_files() === 0) {
    App.file_trigger()
    return false
  }

  if (!App.check_total_size()) {
    return false
  }

  let title = DOM.el(`#title`)

  if (title) {
    if (title.value.length > App.max_title_length) {
      return false
    }
  }

  App.clicked = true
  return true
}

App.reflect_file = (file) => {
  let title = DOM.el(`#title`)

  if (title) {
    title.focus()
  }

  if (!App.check_total_size()) {
    App.reset_file(file)
    App.popmsg(`That file is too big`)
    return false
  }

  App.reset_image()
  App.reset_video()

  let the_file = file.files[0]
  let image = DOM.el(`#image`)
  let video = DOM.el(`#video`)

  if (App.is_image(the_file)) {
    let reader = new FileReader()

    reader.onload = (e) => {
      image.src = e.target.result
    }

    DOM.hide(video)
    DOM.show(image)
    reader.readAsDataURL(the_file)
    App.media_picker = file
  }
  else if (App.is_audio(the_file) || App.is_video(the_file)) {
    video.src = URL.createObjectURL(the_file)
    DOM.hide(image)
    DOM.show(video)
    video.load()
    App.media_picker = file
  }

  return true
}

App.reset_file = (file) => {
  if (file) {
    file.value = null
  }

  App.reset_image()
  App.reset_video()
  DOM.show(`#image`)
}

App.reset_image = () => {
  let image = DOM.el(`#image`)
  image.src = `/static/img/banners/${App.banner}`
}

App.reset_video = () => {
  let video = DOM.el(`#video`)
  video.pause()
  DOM.hide(video)
}

App.add_picker = (show = false) => {
  if (App.num_pickers > 0) {
    let empty = App.get_empty_picker()

    if (empty.files.length === 0) {
      empty.click()
      return
    }
  }

  App.num_pickers += 1

  if (App.num_pickers > App.max_upload_files) {
    return
  }

  let t = DOM.el(`#template_picker`)
  let el = DOM.create(`div`, `picker`)
  el.innerHTML = t.innerHTML
  let input = DOM.el(`input`, el)
  input.id = `file_${App.num_pickers}`
  input.name = `file`

  DOM.ev(el, `change`, (e) => {
    App.clicked = false
    App.remove_duplicate_files()

    if (input.files.length === 0) {
      return
    }

    if (App.reflect_file(input)) {
      App.add_picker()
    }

    App.check_files_used()
  })

  DOM.ev(el, `click`, (e) => {
    if (e.shiftKey || e.ctrlKey || e.altKey) {
      e.preventDefault()
      App.reset_file(input)
    }
    else if (e.target !== input) {
      input.click()
    }
  })

  DOM.ev(el, `auxclick`, (e) => {
    if (e.button === 1) {
      e.preventDefault()
      App.remove_picker(el)
    }
  })

  let c = DOM.el(`#pickers`)
  c.appendChild(el)
  App.on_picker_change()

  if (show) {
    input.click()
  }
}

App.check_compress = () => {
  let checkbox = DOM.el(`#compress`)

  if (!checkbox) {
    return
  }

  if (App.num_active_files() > 1) {
    checkbox.checked = true
    checkbox.disabled = true
    DOM.el(`#zip`).classList.add(`inactive`)
  }
  else {
    checkbox.checked = false
    checkbox.disabled = false
    DOM.el(`#zip`).classList.remove(`inactive`)
  }
}

App.file_trigger = () => {
  let file = App.get_empty_picker()

  if (file) {
    file.click()
  }
}

App.get_empty_picker = () => {
  let files = DOM.els(`.picker_file`)

  for (let file of files) {
    if (file.files.length === 0) {
      return file
    }
  }

  return files[0]
}

App.remove_picker = (picker) => {
  let pickers = DOM.els(`.picker`)

  if (!pickers.length) {
    return
  }

  if (pickers.length === 1) {
    let file = DOM.el(`input`, pickers[0])
    App.reset_file(file)
    return
  }

  if (!picker) {
    picker = pickers.at(-1)
  }

  App.reset_file_media(picker)
  picker.remove()
  App.num_pickers -= 1
  App.on_picker_change()
}

App.check_required_file = () => {
  let files = DOM.els(`.picker_file`)

  for (let [i, file] of files.entries()) {
    if (i === 0) {
      file.required = true
    }
    else {
      file.required = false
    }
  }
}

App.on_picker_change = () => {
  App.check_compress()
  App.check_required_file()
  App.check_files_used()
}

App.reset_file_media = (picker) => {
  let file = DOM.el(`input`, picker)

  if (App.media_picker === file) {
    App.reset_file(file)
  }
}

App.num_active_files = () => {
  let files = DOM.els(`.picker_file`)
  let active = 0

  for (let file of files) {
    let file_length = file.files.length

    if (file_length === 0) {
      continue
    }

    if (file_length > 1) {
      continue
    }

    if (file.files[0].size > App.max_size) {
      continue
    }

    if (!file.files[0].name) {
      continue
    }

    active += 1
  }

  return active
}

App.remove_duplicate_files = () => {
  let files = DOM.els(`.picker_file`)
  let names = []

  for (let file of files) {
    let file_length = file.files.length

    if (file_length === 0) {
      continue
    }

    let name = file.files[0].name

    if (names.includes(name)) {
      App.reset_file(file)
    }

    names.push(name)
  }
}

App.check_files_used = () => {
  let files = DOM.els(`.picker_file`)

  if (files.length < 2) {
    for (let file of files) {
      file.parentElement.classList.remove(`unused`)
    }

    return
  }

  for (let file of files) {
    if (file.files.length === 0) {
      file.parentElement.classList.add(`unused`)
    }
    else {
      file.parentElement.classList.remove(`unused`)
    }
  }
}

App.remove_all_pickers = () => {
  let files = DOM.els(`.picker_file`)

  for (let file of files) {
    App.remove_picker(file.parentElement)
  }
}

App.check_total_size = () => {
  let files = DOM.els(`.picker_file`)
  let total = 0

  for (let file of files) {
    if (file.files.length === 0) {
      continue
    }

    total += file.files[0].size
  }

  return total <= App.max_size
}

App.setup_pickers = () => {
  let add_picker_btn = DOM.el(`#add_picker_btn`)

  if (add_picker_btn) {
    DOM.ev(add_picker_btn, `click`, (e) => {
      App.add_picker(true)
    })
  }

  let remove_picker_btn = DOM.el(`#remove_picker_btn`)

  if (remove_picker_btn) {
    DOM.ev(remove_picker_btn, `click`, (e) => {
      App.remove_picker()
    })

    DOM.ev(remove_picker_btn, `auxclick`, (e) => {
      App.remove_all_pickers()
    })
  }

  if (App.is_user && App.upload_enabled) {
    App.add_picker()
  }
}