App.make_opts = (name, setup, show = false, parent = ``) => {
  let msg_name = `msg_${name}`

  if (App[msg_name]) {
    if (show) {
      App[msg_name].show()
    }

    return
  }

  App[msg_name] = Msg.factory({
    after_show: () => {
      let selection = window.getSelection()
      selection.removeAllRanges()
    },
  })

  let t = DOM.el(`#template_${name}_opts`)
  App[msg_name].set(t.innerHTML)
  setup()

  if (parent) {
    let c = DOM.el(`.dialog_container`, App[msg_name].content)
    let btn = DOM.create(`div`, `aero_button`, `${name}_opts_back`)
    btn.textContent = `Back`
    c.appendChild(btn)

    App.bind_button({
      what: `${name}_opts_back`,
      func: () => {
        App[`setup_${parent}_opts`](true)
      },
      icon: `<`,
    })
  }

  if (show) {
    App[msg_name].show()
  }
}

App.setup_menu_opts = (show = false) => {
  let name = `menu`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_upload`,
      func: () => {
        App.location(`/`)
      },
      mfunc: () => {
        App.open_tab(`/`)
      },
      icon: App.icon(`upload`),
    })

    App.bind_button({
      what: `${name}_opts_fresh`,
      func: () => {
        App.location(`/fresh`)
      },
      mfunc: () => {
        App.open_tab(`/fresh`)
      },
      icon: App.icon(`fresh`),
    })

    App.bind_button({
      what: `${name}_opts_random`,
      func: () => {
        App.show_random()
      },
      mfunc: () => {
        App.random_post()
      },
      icon: App.icon(`random`),
    })

    App.bind_button({
      what: `${name}_opts_list`,
      func: () => {
        App.setup_list_opts(true, name)
      },
      icon: App.icon(`list`),
    })

    App.bind_button({
      what: `${name}_opts_admin`,
      func: () => {
        App.setup_admin_opts(true, name)
      },
      icon: App.icon(`admin`),
    })

    App.bind_button({
      what: `${name}_opts_search`,
      func: () => {
        App.setup_search_opts(true, name)
      },
      icon: App.icon(`search`),
    })

    App.bind_button({
      what: `${name}_opts_links`,
      func: () => {
        App.setup_link_opts(true, name)
      },
      icon: App.icon(`links`),
    })

    App.bind_button({
      what: `${name}_opts_you`,
      func: () => {
        App.setup_you_opts(App.user_id, true, name)
      },
      icon: App.icon(`you`),
    })

    App.bind_button({
      what: `${name}_opts_login`,
      func: () => {
        App.location(`/login`)
      },
      mfunc: () => {
        App.open_tab(`/login`)
      },
    })

    App.bind_button({
      what: `${name}_opts_register`,
      func: () => {
        App.location(`/register`)
      },
      mfunc: () => {
        App.open_tab(`/register`)
      },
    })
  }, show)
}

App.setup_you_opts = (user_id, show = false, parent = ``) => {
  let name = `you`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_posts`,
      func: () => {
        App.location(`/list/posts?user_id=${user_id}`)
      },
      icon: App.icon(`posts`),
    })

    App.bind_button({
      what: `${name}_opts_reactions`,
      func: () => {
        App.location(`/list/reactions?user_id=${user_id}`)
      },
      icon: App.icon(`reactions`),
    })

    App.bind_button({
      what: `${name}_opts_edit_name`,
      func: () => {
        App.edit_name()
      },
      icon: App.icon(`edit`),
      close: false,
    })

    App.bind_button({
      what: `${name}_opts_edit_password`,
      func: () => {
        App.edit_password()
      },
      icon: App.icon(`edit`),
      close: false,
    })

    App.bind_button({
      what: `${name}_opts_edit_settings`,
      func: () => {
        App.show_settings()
      },
      icon: App.icon(`settings`),
    })

    App.bind_button({
      what: `${name}_opts_logout`,
      func: () => {
        let confirm_args = {
          message: `Visne profecto discedere`,
          callback_yes: () => {
            App.location(`/logout`)
          },
        }

        App.confirmbox(confirm_args)
      },
      icon: App.icon(`logout`),
    })
  }, show, parent)
}

App.setup_sort_opts = (show = false) => {
  let name = `sort`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_asc_all`,
      func: () => {
        App.sort_action(App.sort_what, false, false)
      },
      icon: App.icon(`asc`, false),
    })

    App.bind_button({
      what: `${name}_opts_desc_all`,
      func: () => {
        App.sort_action(App.sort_what, true)
      },
      icon: App.icon(`desc`),
    })

    App.bind_button({
      what: `${name}_opts_asc_page`,
      func: () => {
        App.sort_action(App.sort_what, false, true)
      },
      icon: App.icon(`asc`, false),
    })

    App.bind_button({
      what: `${name}_opts_desc_page`,
      func: () => {
        App.sort_action(App.sort_what, true, true)
      },
      icon: App.icon(`desc`),
    })
  }, show)
}

App.setup_user_opts = (show = false, parent = ``) => {
  let name = `user`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_posts`,
      func: () => {
        if (!App.is_reader) {
          App.login_feedback()
          return
        }

        let user_id = App.user_opts_user_id

        if (App.mode.includes(`admin`)) {
          App.location(`/admin/posts?user_id=${user_id}`)
        }
        else {
          App.location(`/list/posts?user_id=${user_id}`)
        }
      },
      mfunc: () => {
        if (!App.is_reader) {
          App.login_feedback()
          return
        }

        let user_id = App.user_opts_user_id

        if (App.mode.includes(`admin`)) {
          App.open_tab(`/admin/posts?user_id=${user_id}`)
        }
        else {
          App.open_tab(`/list/posts?user_id=${user_id}`)
        }
      },
      icon: App.icon(`posts`),
    })

    App.bind_button({
      what: `${name}_opts_reactions`,
      func: () => {
        if (!App.is_reader) {
          App.login_feedback()
          return
        }

        let user_id = App.user_opts_user_id

        if (App.mode.includes(`admin`)) {
          App.location(`/admin/reactions?user_id=${user_id}`)
        }
        else {
          App.location(`/list/reactions?user_id=${user_id}`)
        }
      },
      mfunc: () => {
        if (!App.is_reader) {
          App.login_feedback()
          return
        }

        let user_id = App.user_opts_user_id

        if (App.mode.includes(`admin`)) {
          App.open_tab(`/admin/reactions?user_id=${user_id}`)
        }
        else {
          App.open_tab(`/list/reactions?user_id=${user_id}`)
        }
      },
      icon: App.icon(`reactions`),
    })

    App.bind_button({
      what: `${name}_opts_user`,
      func: () => {
        if (!App.is_reader) {
          App.login_feedback()
          return
        }

        let user_id = App.user_opts_user_id
        App.location(`/edit_user/${user_id}`)
      },
      mfunc: () => {
        if (!App.is_reader) {
          App.login_feedback()
          return
        }

        let user_id = App.user_opts_user_id
        App.open_tab(`/edit_user/${user_id}`)
      },
      icon: App.icon(`edit`),
    })
  }, show, parent)
}

App.setup_reaction_opts = (show = false) => {
  let name = `reaction`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_edit`,
      func: () => {
        let id = App.active_item.dataset.id
        App.react_prompt(id)
      },
      icon: App.icon(`edit`),
    })

    App.bind_button({
      what: `${name}_opts_delete`,
      func: () => {
        let id = App.active_item.dataset.id
        App.delete_reaction(id)
      },
      icon: App.icon(`delete`),
    })
  }, show)
}

App.setup_list_opts = (show = false, parent = ``) => {
  let name = `list`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_posts`,
      func: () => {
        App.location(`/list/posts`)
      },
      mfunc: () => {
        App.open_tab(`/list/posts`)
      },
      icon: App.icon(`posts`),
    })

    App.bind_button({
      what: `${name}_opts_reactions`,
      func: () => {
        App.location(`/list/reactions`)
      },
      mfunc: () => {
        App.open_tab(`/list/reactions`)
      },
      icon: App.icon(`reactions`),
    })
  }, show, parent)
}

App.setup_random_opts = (show = false, parent = ``) => {
  let name = `random`

  function make(type) {
    let cls = ``

    if (App.post && (type === App.post.media_type)) {
      cls = `button_highlight`
    }

    App.bind_button({
      what: `${name}_opts_${type}`,
      func: () => {
        App.random_action(type)
      },
      mfunc: () => {
        App.random_action(type, true)
      },
      icon: App.media_icon(type),
      class: cls,
    })
  }

  App.make_opts(name, () => {
    make(`any`)
    make(`video`)
    make(`audio`)
    make(`image`)
    make(`text`)
    make(`talk`)
    make(`flash`)
    make(`zip`)
    make(`url`)
  }, show, parent)
}

App.setup_next_opts = (show = false, parent = ``) => {
  let name = `next`

  function make(type) {
    let cls = ``

    if (App.post && (type === App.post.media_type)) {
      cls = `button_highlight`
    }

    App.bind_button({
      what: `${name}_opts_${type}`,
      func: () => {
        App.next_action(type)
      },
      mfunc:() => {
        App.next_action(type, true)
      },
      icon: App.media_icon(type),
      class: cls,
    })
  }

  App.make_opts(name, () => {
    make(`any`)
    make(`video`)
    make(`audio`)
    make(`image`)
    make(`text`)
    make(`talk`)
    make(`flash`)
    make(`zip`)
    make(`url`)
  }, show, parent)
}

App.setup_admin_opts = (show = false, parent = ``) => {
  let name = `admin`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_posts`,
      func: () => {
        App.location(`/admin/posts`)
      },
      mfunc: () => {
        App.open_tab(`/admin/posts`)
      },
      icon: App.icon(`posts`),
    })

    App.bind_button({
      what: `${name}_opts_reactions`,
      func: () => {
        App.location(`/admin/reactions`)
      },
      mfunc: () => {
        App.open_tab(`/admin/reactions`)
      },
      icon: App.icon(`reactions`),
    })

    App.bind_button({
      what: `${name}_opts_users`,
      func: () => {
        App.location(`/admin/users`)
      },
      mfunc: () => {
        App.open_tab(`/admin/users`)
      },
      icon: App.icon(`users`),
    })
  }, show, parent)
}

App.setup_link_opts = (show = false, parent = ``) => {
  let name = `link`

  App.make_opts(name, () => {
    let c = DOM.el(`#links_container`)

    for (let [i, link] of App.links.entries()) {
      let item = DOM.create(`div`, `aero_button`, `${name}_opts_${i}`)
      item.textContent = link.name
      item.title = link.url
      c.appendChild(item)

      App.bind_button({
        what: `${name}_opts_${i}`,
        func: () => {
          App.open_tab(link.url, link.target)
        },
        mfunc: () => {
          App.open_tab(link.url)
        },
        icon: link.icon,
      })
    }
  }, show, parent)
}

App.setup_edit_post_opts = (show = false) => {
  let name = `edit_post`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_title`,
      func: () => {
        App.edit_title()
      },
      icon: App.icon(`edit`),
    })

    App.bind_button({
      what: `${name}_opts_description`,
      func: () => {
        App.edit_description()
      },
      icon: App.icon(`edit`),
    })

    App.bind_button({
      what: `${name}_opts_filename`,
      func: () => {
        App.edit_filename()
      },
      icon: App.icon(`filename`),
    })

    App.bind_button({
      what: `${name}_opts_privacy`,
      func: () => {
        App.setup_edit_privacy_opts(true, name)
      },
      icon: App.icon(App.post.privacy),
    })

    App.bind_button({
      what: `${name}_opts_delete`,
      func: () => {
        App.delete_post()
      },
      icon: App.icon(`delete`),
    })
  }, show)
}

App.setup_edit_privacy_opts = (show = false, parent = ``) => {
  let name = `edit_privacy`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_public`,
      func: () => {
        App.edit_privacy(`public`)
      },
      icon: App.icon(`public`),
    })

    App.bind_button({
      what: `${name}_opts_private`,
      func: () => {
        App.edit_privacy(`private`)
      },
      icon: App.icon(`private`),
    })
  }, show, parent)
}

App.setup_user_edit_opts = (show = false) => {
  let name = `user_edit`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_poster_no`,
      func: () => {
        App.mod_user(`poster`, 0, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_reader_no`,
      func: () => {
        App.mod_user(`reader`, 0, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_reader_yes`,
      func: () => {
        App.mod_user(`reader`, 1, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_lister_no`,
      func: () => {
        App.mod_user(`lister`, 0, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_lister_yes`,
      func: () => {
        App.mod_user(`lister`, 1, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_reacter_no`,
      func: () => {
        App.mod_user(`reacter`, 0, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_reacter_yes`,
      func: () => {
        App.mod_user(`reacter`, 1, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_mage_no`,
      func: () => {
        App.mod_user(`mage`, 0, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_mage_yes`,
      func: () => {
        App.mod_user(`mage`, 1, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_admin_no`,
      func: () => {
        App.mod_user(`admin`, 0, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_admin_yes`,
      func: () => {
        App.mod_user(`admin`, 1, `bool`)
      },
    })

    App.bind_button({
      what: `${name}_opts_rpm`,
      func: () => {
        App.user_mod_input(`rpm`, ``, `number`)
      },
    })

    App.bind_button({
      what: `${name}_opts_max_size`,
      func: () => {
        App.user_mod_input(`max_size`, ``, `number`)
      },
    })

    App.bind_button({
      what: `${name}_opts_mark`,
      func: () => {
        App.user_mod_input(`mark`, ``, `string`)
      },
    })

    App.bind_button({
      what: `${name}_opts_name`,
      func: () => {
        App.user_mod_input(`name`, ``, `string`)
      },
    })

    App.bind_button({
      what: `${name}_opts_username`,
      func: () => {
        App.user_mod_input(`username`, ``, `string`)
      },
    })

    App.bind_button({
      what: `${name}_opts_password`,
      func: () => {
        App.user_mod_input(`password`, ``, `password`)
      },
    })
  }, show)
}

App.setup_post_edit_opts = (show = false) => {
  let name = `post_edit`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_title`,
      func: () => {
        App.edit_post_title()
      },
      icon: App.icon(`edit`),
    })

    App.bind_button({
      what: `${name}_opts_public`,
      func: () => {
        App.edit_post_privacy(`public`)
      },
      icon: App.icon(`public`),
    })

    App.bind_button({
      what: `${name}_opts_private`,
      func: () => {
        App.edit_post_privacy(`private`)
      },
      icon: App.icon(`private`),
    })
  }, show)
}

App.setup_page_opts = (show = false) => {
  let name = `page`

  function make(num) {
    App.bind_button({
      what: `${name}_opts_${num}`,
      func: () => {
        App.goto_page(num)
      },
      mfunc: () => {
        App.goto_page(num, true)
      },
      icon: App.icon(`page`),
    })
  }

  App.make_opts(name, () => {
    for (let n = 1; n <= 9; n++) {
      make(n)
    }
  }, show)
}

App.setup_volume_opts = (show = false) => {
  let icon
  let name = `volume`

  function make(num) {
    if (num > 75) {
      icon = `volume_max`
    }
    else if ((num <= 75) && (num > 25)) {
      icon = `volume_mid`
    }
    else if (num > 0) {
      icon = `volume_min`
    }
    else {
      icon = `volume_muted`
    }

    let vol = num / 100

    App.bind_button({
      what: `${name}_opts_${num}`,
      func: () => {
        App.set_volume(vol)
      },
      mfunc: () => {
        App.set_volume(vol, true)
      },
      icon: App.icon(icon),
    })
  }

  App.make_opts(name, () => {
    for (let n of [100, 75, 50, 25, 0]) {
      make(n)
    }
  }, show)
}

App.setup_search_opts = (show = false) => {
  let name = `search`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_posts`,
      func: () => {
        App.prompt_search(`posts`)
      },
      icon: App.icon(`posts`),
    })

    App.bind_button({
      what: `${name}_opts_reactions`,
      func: () => {
        App.prompt_search(`reactions`)
      },
      icon: App.icon(`reactions`),
    })

    App.bind_button({
      what: `${name}_opts_users`,
      func: () => {
        App.prompt_search(`users`)
      },
      icon: App.icon(`users`),
    })
  }, show, `menu`)
}

App.setup_video_commands_opts = (show = false, parent = ``) => {
  let name = `video_commands`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_jump`,
      func: () => {
        App.video_jump()
      },
      icon: App.icon(`jump`),
    })

    App.bind_button({
      what: `${name}_opts_rewind`,
      func: () => {
        App.video_rewind()
      },
      icon: App.icon(`rewind`),
    })

    App.bind_button({
      what: `${name}_opts_slower`,
      func: () => {
        App.video_slow()
      },
      icon: App.icon(`slow`),
      close: false,
    })

    App.bind_button({
      what: `${name}_opts_faster`,
      func: () => {
        App.video_fast()
      },
      icon: App.icon(`fast`),
      close: false,
    })

    App.bind_button({
      what: `${name}_opts_fade_in`,
      func: () => {
        App.video_fade_in()
      },
      icon: App.icon(`fade_in`),
    })

    App.bind_button({
      what: `${name}_opts_fade_out`,
      func: () => {
        App.video_fade_out()
      },
      icon: App.icon(`fade_out`),
    })
  }, show, parent)
}

App.setup_zip_file_opts = (show = false, parent = ``) => {
  let name = `zip_file`

  App.make_opts(name, () => {
    App.bind_button({
      what: `${name}_opts_list`,
      func: () => {
        App.list_zip()
      },
      icon: App.icon(`read`),
    })

    App.bind_button({
      what: `${name}_opts_download`,
      func: () => {
        App.download_file(false, true)
      },
      icon: App.icon(`download`),
    })
  }, show, parent)
}