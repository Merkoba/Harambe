App.init = () => {
  App.clicked = false

  window.addEventListener(`pageshow`, (e) => {
    App.close_modals()
    App.clicked = false
  })

  App.setup_dragdrop()
  App.setup_image()
  App.setup_video()
  App.setup_menu()
  App.setup_non_user()
  App.setup_submit()
  App.setup_zip()
  App.setup_pickers()
  App.setup_keys()
  App.setup_pastebin()
  App.setup_description()
  App.focus_title()
}

App.validate = () => {
  if (App.clicked) {
    App.print_info(`Validate: Clicked`)
    return false
  }

  let title = DOM.el(`#title`)
  let title_is_url = false

  if (title) {
    if (title.value.length > App.max_title_length) {
      App.popmsg(`Title is too long`)
      return false
    }

    title_is_url = App.is_a_url(title.value)

    if (!title_is_url) {
      if (App.contains_url(title.value)) {
        App.popmsg(`Title cannot contain a url`)
        return false
      }
    }
  }

  let description = DOM.el(`#description`)

  if (description) {
    if (description.value.length > App.max_description_length) {
      App.popmsg(`Description is too long`)
      return false
    }
  }

  let texts = App.get_texts()

  if (App.num_active_files() === 0) {
    if (!title_is_url && !description.value.trim() && !texts.length) {
      App.file_trigger()
      App.popmsg(`Upload something first`)
      return false
    }
  }

  if (!App.check_total_size()) {
    App.popmsg(`Total size is too big`)
    return false
  }

  if (texts.length) {
    for (let text of texts) {
      if (text.length > App.max_pastebin_length) {
        App.popmsg(`Text is too long`)
        return false
      }
    }
  }

  App.clicked = true

  if (App.is_mage) {
    App.clicked = false
    return App.check_magic()
  }

  App.uploading()
  return true
}

App.submit_form = (check = true) => {
  if (check && !App.validate()) {
    return
  }

  App.uploading()
  DOM.el(`#form`).submit()
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

  App.check_file_media(file)
  return true
}

App.reset_file = (file) => {
  if (file) {
    file.value = null
  }

  App.reset_image()
  App.reset_video()
  DOM.show(`#image`)
  App.check_files_used()
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

App.num_pickers = () => {
  return DOM.els(`.picker`).length
}

App.add_picker = (show = false) => {
  let num_pickers = App.num_pickers()

  if (show && (num_pickers > 0)) {
    let empty = App.get_empty_picker()

    if (empty.files.length === 0) {
      empty.click()
      return empty
    }
  }

  if (num_pickers >= App.max_upload_files) {
    return
  }

  let t = DOM.el(`#template_picker`)
  let el = DOM.create(`div`, `picker`)
  el.innerHTML = t.innerHTML
  let input = DOM.el(`input`, el)
  input.id = `file_${num_pickers}`
  input.name = `file`
  let file = DOM.el(`.picker_file`, el)

  DOM.ev(el, `change`, (e) => {
    App.clicked = false
    App.remove_duplicate_files()
    App.check_multi_files(input)

    if (App.reflect_file(input)) {
      App.add_picker()
    }

    App.check_files_used()
    App.file_title(file)
  })

  DOM.ev(el, `click`, (e) => {
    if (e.shiftKey || e.ctrlKey || e.altKey) {
      e.preventDefault()
      App.reset_file(input)
    }
  })

  DOM.ev(el, `auxclick`, (e) => {
    if (e.button === 1) {
      e.preventDefault()
      App.remove_picker(el)
    }
  })

  let clear = DOM.el(`.picker_clear`, el)

  DOM.ev(clear, `click`, (e) => {
    App.reset_file(input)
  })

  let title = DOM.el(`.picker_title`, el)

  DOM.ev(title, `click`, (e) => {
    if (input.files.length > 0) {
      App.set_title(App.get_file_title(input.files[0]))
    }
  })

  let view = DOM.el(`.picker_view`, el)

  DOM.ev(view, `click`, (e) => {
    if (input.files.length > 0) {
      App.check_file_media(input)
    }
  })

  let remove = DOM.el(`.picker_remove`, el)

  DOM.ev(remove, `click`, (e) => {
    App.remove_picker(el)
  })

  let c = DOM.el(`#pickers`)
  c.appendChild(el)
  App.on_picker_change()

  if (show) {
    input.click()
  }

  return file
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
  App.on_picker_change()
}

App.on_picker_change = () => {
  App.check_files_used()
}

App.reset_file_media = (picker) => {
  let file = DOM.el(`input`, picker)

  if (App.media_picker === file) {
    App.reset_file(file)
  }
}

App.num_active_files = () => {
  return App.get_active_files().length
}

App.get_active_files = () => {
  let files = DOM.els(`.picker_file`)
  let active = []

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

    active.push(file)
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

  for (let file of files) {
    if (file.files.length === 0) {
      file.parentElement.classList.add(`unused`)
    }
    else {
      file.parentElement.classList.remove(`unused`)
    }
  }

  let c = DOM.el(`#pickers`)

  if ((files.length === 1) && (files[0].files.length === 0)) {
    c.classList.add(`empty`)
  }
  else {
    c.classList.remove(`empty`)
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

App.check_media_magic = (what) => {
  if (!App[`${what}_magic_enabled`]) {
    return false
  }

  let checkbox = DOM.el(`#${what}_magic`)

  if (!checkbox) {
    return
  }

  let files = App.get_active_files()

  if (files.length !== 1) {
    return false
  }

  let file = files[0].files[0]
  let min_size = App[`${what}_magic_min_size`]

  if (min_size > 0) {
    if (file.size > min_size) {
      return false
    }
  }

  if (!App[`is_${what}`](file, false)) {
    return false
  }

  return App[`is_lossless_${what}`](file)
}

App.check_album_magic = () => {
  if (!App.album_magic_enabled) {
    return false
  }

  let checkbox = DOM.el(`#album_magic`)

  if (!checkbox) {
    return
  }

  let audio_count = 0

  for (let file of App.get_active_files()) {
    let current = file.files[0]

    if (App.is_audio(current)) {
      audio_count++
    }
    else {
      return false
    }
  }

  return audio_count > 1
}

App.check_visual_magic = () => {
  if (!App.visual_magic_enabled) {
    return false
  }

  let checkbox = DOM.el(`#visual_magic`)

  if (!checkbox) {
    return
  }

  let image_count = 0
  let audio_count = 0

  for (let file of App.get_active_files()) {
    let current = file.files[0]

    if (App.is_image(current)) {
      image_count++
    }
    else if (App.is_audio(current)) {
      audio_count++
    }
    else {
      return false
    }
  }

  if (image_count !== 1) {
    return false
  }

  return audio_count >= 1
}

App.check_gif_magic = () => {
  if (!App.gif_magic_enabled) {
    return false
  }

  let checkbox = DOM.el(`#gif_magic`)

  if (!checkbox) {
    return
  }

  let image_count = 0

  for (let file of App.get_active_files()) {
    let current = file.files[0]

    if (App.is_image(current, false)) {
      image_count++
    }
    else {
      return false
    }
  }

  return image_count >= 2
}

App.check_magic = () => {
  if (!App.magic_enabled || !App.is_mage) {
    return true
  }

  if (DOM.el(`#zip`).checked) {
    return true
  }

  function check_media(what, msg) {
    let cb = DOM.el(`#${what}_magic`)
    let ok = false

    if (what === `album`) {
      ok = App.check_album_magic()
    }
    else if (what === `visual`) {
      ok = App.check_visual_magic()
    }
    else if (what === `gif`) {
      ok = App.check_gif_magic()
    }
    else {
      ok = App.check_media_magic(what)
    }

    if (!ok) {
      return false
    }

    let confirm_args = {
      message: `Do <b>${what}</b> magic\n
      ${msg}`,
      callback_yes: () => {
        cb.checked = true
        App.submit_form(false)
      },
      callback_no: () => {
        cb.checked = false
        App.submit_form(false)
      },
      yes: `Do that`,
      no: `Just Upload`,
    }

    App.confirmbox(confirm_args)
    return true
  }

  if (check_media(`image`,
    `This means the image will be converted to a jpg`)) {
    return false
  }

  if (check_media(`audio`,
    `This means the audio will be converted to an mp3`)) {
    return false
  }

  if (check_media(`video`,
    `This means the video will be converted to an mp4`)) {
    return false
  }

  if (check_media(`album`,
    `This means the audio tracks will be joined into an mp3`)) {
    return false
  }

  if (check_media(`visual`,
    `This means the image and audio tracks will be joined into an mp4`)) {
    return false
  }

  if (check_media(`gif`,
    `This means the images will be joined into a gif`)) {
    return false
  }

  return true
}

App.uploading = () => {
  App.flash(`Upload in progress`)
  document.title = document.title + ` | Uploading`
}

App.set_title = (title) => {
  let input = DOM.el(`#title`)

  if (input) {
    input.value = title.trim()
  }
}

App.check_file_media = (file) => {
  let the_file = file.files[0]
  let image = DOM.el(`#image`)
  let video = DOM.el(`#video`)

  if (App.is_image(the_file)) {
    let reader = new FileReader()

    reader.onload = (e) => {
      image.src = e.target.result
      DOM.show(image)
    }

    App.reset_video()
    reader.readAsDataURL(the_file)
    App.media_picker = file
  }
  else if (App.is_audio(the_file) || App.is_video(the_file)) {
    let reader = new FileReader()

    reader.onload = (e) => {
      video.src = URL.createObjectURL(the_file)
      DOM.show(video)
    }

    DOM.hide(image)
    reader.readAsDataURL(the_file)
    App.media_picker = file
  }
}

App.get_file_title = (file) => {
  let split = file.name.split(`.`)
  return split.slice(0, -1).join(`.`)
}

App.setup_zip = () => {
  let zip = DOM.el(`#zip_container`)

  DOM.ev(zip, `click`, (e) => {
    if (e.target.id === `zip`) {
      return
    }

    DOM.el(`#zip`).click()
  })
}

App.setup_submit = () => {
  let submit_btn = DOM.el(`#submit_btn`)

  if (submit_btn) {
    DOM.ev(submit_btn, `click`, (e) => {
      App.submit_form()
    })

    DOM.ev(submit_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.remove_picker()
      }
    })
  }
}

App.setup_non_user = () => {
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
}

App.setup_menu = () => {
  let menu_btn = DOM.el(`#menu_btn`)

  if (menu_btn) {
    App.setup_menu_opts(false, [`upload`])

    DOM.ev(menu_btn, `click`, (e) => {
      App.msg_show(`menu`)
    })

    DOM.ev(menu_btn, `auxclick`, (e) => {
      if (e.button === 1) {
        App.msg_show(`menu`)
      }
    })
  }
}

App.setup_image = () => {
  let image = DOM.el(`#image`)

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
}

App.setup_video = () => {
  let video = DOM.el(`#video`)

  if (video) {
    DOM.ev(video, `auxclick`, (e) => {
      App.reset_file()
    })

    DOM.ev(video, `error`, (e) => {
      App.reset_file()
    })
  }
}

App.setup_dragdrop = () => {
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
}

App.get_texts = () => {
  let texts = []
  let pastebins = DOM.els(`.pastebin`)

  for (let pastebin of pastebins) {
    if (pastebin.value.trim()) {
      texts.push(pastebin.value)
    }
  }

  return texts
}

App.setup_keys = (e) => {
  function action_1() {
    App.submit_form()
  }

  function action_2(e) {
    if (e.ctrlKey || e.shiftKey) {
      App.submit_form()
    }
  }

  DOM.ev(document.querySelector(`#form`), `keydown`, (e) => {
    if (e.key === `Enter`) {
      if (e.id === `form`) {
        e.preventDefault()
      }
    }
  })

  DOM.ev(document, `keydown`, (e) => {
    if (e.key === `Enter`) {
      if ([`title`].includes(e.target.id)) {
        action_1(e)
      }
      else if ([`description`].includes(e.target.id)) {
        action_2(e)
      }
      else if ([`pastebin_filename`].some(cls => e.target.classList.contains(cls))) {
        action_1(e)
      }
      else if ([`pastebin`].some(cls => e.target.classList.contains(cls))) {
        action_2(e)
      }
    }
  })
}

App.setup_pastebin = () => {
  let menu_text = DOM.el(`#menu_text`)

  if (menu_text) {
    DOM.ev(menu_text, `click`, (e) => {
      App.add_pastebin()
    })

    DOM.ev(menu_text, `auxclick`, (e) => {
      App.remove_pastebin()
    })
  }
}

App.add_pastebin = () => {
  let t = DOM.el(`#template_pastebin`)
  let c = DOM.create(`div`, `pastebin_container`)
  c.innerHTML = t.innerHTML
  let main = DOM.el(`#pastebins`)
  main.appendChild(c)
  let max = DOM.el(`.pastebin_max`, c)

  DOM.ev(max, `click`, (e) => {
    App.toggle_max_pastebin(c)
  })

  let remove = DOM.el(`.pastebin_remove`, c)

  DOM.ev(remove, `click`, (e) => {
    App.remove_pastebin(c)
  })

  let clear = DOM.el(`.pastebin_clear`, c)

  DOM.ev(clear, `click`, (e) => {
    App.clear_pastebin(c)
  })

  let text = DOM.el(`.pastebin`, c)

  DOM.ev(text, `blur`, () => {
    text.value = App.untab_string(text.value)
  })

  DOM.show(main)
  App.to_bottom()
  text.focus()
}

App.remove_pastebin = (c) => {
  let pastebins = DOM.els(`.pastebin_container`)
  let length = pastebins.length

  if (!length) {
    return
  }

  if (c) {
    c.remove()
  }
  else {
    pastebins.at(-1).remove()
  }

  if (length === 1) {
    DOM.hide(`#pastebins`)
  }
}

App.toggle_max_pastebin = (c) => {
  c.classList.toggle(`max`)
  App.focus_pastebin(c)
}

App.clear_pastebin = (c) => {
  let pastebin = DOM.el(`.pastebin`, c)
  pastebin.value = ``
  App.focus_pastebin(c)
}

App.focus_pastebin = (c) => {
  let pastebin = DOM.el(`.pastebin`, c)
  pastebin.focus()
}

App.focus_title = () => {
  DOM.el(`#title`).focus()
}

App.setup_description = () => {
  let description = DOM.el(`#description`)

  if (description) {
    DOM.ev(description, `blur`, (e) => {
      description.value = App.untab_string(description.value)
    })
  }
}

App.check_multi_files = (input) => {
  if (input.files.length <= 1) {
    return
  }

  let files = Array.from(input.files)
  let data_transfer = new DataTransfer()
  data_transfer.items.add(files[0])
  input.files = data_transfer.files
  files.shift()

  for (let file of files) {
    let picker = App.add_picker()

    if (picker) {
      let new_data_transfer = new DataTransfer()
      new_data_transfer.items.add(file)
      picker.files = new_data_transfer.files
      App.reflect_file(picker)
      App.file_title(picker)
    }
  }
}

App.file_title = (input) => {
  let file = input.files[0]
  input.title = `${file.name} | ${App.size_string(file.size)}`
}