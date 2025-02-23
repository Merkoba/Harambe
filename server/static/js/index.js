let clicked = false

window.onload = () => {
  let image = DOM.el(`#image`)

  if (image) {
    DOM.ev(image, `click`, (e) => {
      if (!vars.is_user) {
        popmsg(`Login or register first.`)
        return
      }

      if (e.shiftKey || e.ctrlKey || e.altKey) {
        reset_file()
        return
      }

      let file = DOM.el(`#file`)
      file.click()
    })

    DOM.ev(image, `auxclick`, (e) => {
      if (e.button === 1) {
        e.preventDefault()
        reset_file()
      }
    })

    let file = DOM.el(`#file`)

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

  let more_links = DOM.el(`#more_links`)

  if (more_links) {
    vars.msg_links = Msg.factory()
    let t = DOM.el(`#template_links`)
    vars.msg_links.set(t.innerHTML)
    let c = DOM.el(`#more_links_container`)

    for (let link of vars.links) {
      let item = DOM.create(`div`, `aero_button`)
      item.textContent = link.name
      item.title = link.url

      DOM.ev(item, `click`, (e) => {
        vars.msg_links.close()
        window.open(link.url, item.target)
      })

      c.appendChild(item)
    }

    DOM.ev(more_links, `click`, (e) => {
      vars.msg_links.show()
    })
  }

  let admin_opts = DOM.el(`#template_admin_opts`)

  if (admin_opts) {
    setup_admin_opts()

    DOM.ev(`#admin_btn`, `click`, (e) => {
      vars.msg_admin_opts.show()
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
    popmsg(`That file is too big.`)
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
  image.src = `static/img/${vars.image_name}`
}

function reset_video() {
  let video = DOM.el(`#video`)
  video.pause()
  DOM.hide(video)
}

function show_links() {
  let links_dialog = DOM.el(`#links_dialog`)
  links_dialog.showModal()
}