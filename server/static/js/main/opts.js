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

    App.bind_button(`${name}_opts_back`, () => {
      App[`setup_${parent}_opts`](true)
    }, undefined, `<`)
  }

  if (show) {
    App[msg_name].show()
  }
}

App.setup_menu_opts = (show = false, ignore = []) => {
  let name = `menu`

  App.make_opts(name, () => {
    App.ignore_buttons(name, ignore)

    App.bind_button(`${name}_opts_upload`, () => {
      App.location(`/`)
    }, () => {
      App.open_tab(`/`)
    }, App.icon(`upload`))

    App.bind_button(`${name}_opts_fresh`, () => {
      App.location(`/fresh`)
    }, () => {
      App.open_tab(`/fresh`)
    }, App.icon(`fresh`))

    App.bind_button(`${name}_opts_random`, () => {
      App.show_random()
    }, () => {
      App.random_post()
    }, App.icon(`random`))

    App.bind_button(`${name}_opts_list`, () => {
      App.setup_list_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_admin`, () => {
      App.setup_admin_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_search`, () => {
      App.setup_search_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_links`, () => {
      App.setup_link_opts(true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_you`, () => {
      App.setup_you_opts(App.user_id, true, name)
    }, undefined, `>`)

    App.bind_button(`${name}_opts_login`, () => {
      App.location(`/login`)
    }, () => {
      App.open_tab(`/login`)
    })

    App.bind_button(`${name}_opts_register`, () => {
      App.location(`/register`)
    }, () => {
      App.open_tab(`/register`)
    })
  }, show)
}

App.setup_you_opts = (user_id, show = false, parent = ``) => {
  let name = `you`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.location(`/list/posts?user_id=${user_id}`)
    }, undefined, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.location(`/list/reactions?user_id=${user_id}`)
    }, undefined, App.icon(`reactions`))

    App.bind_button(`${name}_opts_edit_name`, () => {
      App.edit_name()
    }, undefined, App.icon(`edit`), false)

    App.bind_button(`${name}_opts_edit_password`, () => {
      App.edit_password()
    }, undefined, App.icon(`edit`), false)

    App.bind_button(`${name}_opts_edit_settings`, () => {
      App.show_settings()
    }, undefined, App.icon(`settings`))

    App.bind_button(`${name}_opts_logout`, () => {
      let confirm_args = {
        message: `Visne profecto discedere`,
        callback_yes: () => {
          App.location(`/logout`)
        },
      }

      App.confirmbox(confirm_args)
    }, undefined, App.icon(`logout`))
  }, show, parent)
}

App.setup_sort_opts = (show = false) => {
  let name = `sort`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_asc_all`, () => {
      App.sort_action(App.sort_what, false, false)
    }, undefined, App.icon(`asc`, false))

    App.bind_button(`${name}_opts_desc_all`, () => {
      App.sort_action(App.sort_what, true)
    }, undefined, App.icon(`desc`))

    App.bind_button(`${name}_opts_asc_page`, () => {
      App.sort_action(App.sort_what, false, true)
    }, undefined, App.icon(`asc`, false))

    App.bind_button(`${name}_opts_desc_page`, () => {
      App.sort_action(App.sort_what, true, true)
    }, undefined, App.icon(`desc`))
  }, show)
}

App.setup_user_opts = (show = false, parent = ``) => {
  let name = `user`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
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
    }, () => {
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
    }, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
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
    }, () => {
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
    }, App.icon(`reactions`))

    App.bind_button(`${name}_opts_user`, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id
      App.location(`/edit_user/${user_id}`)
    }, () => {
      if (!App.is_reader) {
        App.login_feedback()
        return
      }

      let user_id = App.user_opts_user_id
      App.open_tab(`/edit_user/${user_id}`)
    }, App.icon(`edit`))
  }, show, parent)
}

App.setup_reaction_opts = (show = false) => {
  let name = `reaction`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_edit`, () => {
      let id = App.active_item.dataset.id
      App.react_prompt(id)
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_delete`, () => {
      let id = App.active_item.dataset.id
      App.delete_reaction(id)
    }, undefined, App.icon(`delete`))
  }, show)
}

App.setup_list_opts = (show = false, parent = ``) => {
  let name = `list`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.location(`/list/posts`)
    }, () => {
      App.open_tab(`/list/posts`)
    }, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.location(`/list/reactions`)
    }, () => {
      App.open_tab(`/list/reactions`)
    }, App.icon(`reactions`))
  }, show, parent)
}

App.setup_random_opts = (show = false, parent = ``) => {
  let name = `random`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_any`, () => {
      App.random_action(`random`)
    }, () => {
      App.random_action(`random`, true)
    }, App.icon(`random`))

    App.bind_button(`${name}_opts_video`, () => {
      App.random_action(`video`)
    }, () => {
      App.random_action(`video`, true)
    }, App.icon(`video`))

    App.bind_button(`${name}_opts_audio`, () => {
      App.random_action(`audio`)
    }, () => {
      App.random_action(`audio`, true)
    }, App.icon(`audio`))

    App.bind_button(`${name}_opts_image`, () => {
      App.random_action(`image`)
    }, () => {
      App.random_action(`image`, true)
    }, App.icon(`image`))

    App.bind_button(`${name}_opts_text`, () => {
      App.random_action(`text`)
    }, () => {
      App.random_action(`text`, true)
    }, App.icon(`text`))

    App.bind_button(`${name}_opts_talk`, () => {
      App.random_action(`talk`)
    }, () => {
      App.random_action(`talk`, true)
    }, App.icon(`talk`))

    App.bind_button(`${name}_opts_flash`, () => {
      App.random_action(`flash`)
    }, () => {
      App.random_action(`flash`, true)
    }, App.icon(`flash`))

    App.bind_button(`${name}_opts_zip`, () => {
      App.random_action(`zip`)
    }, () => {
      App.random_action(`zip`, true)
    }, App.icon(`zip`))

    App.bind_button(`${name}_opts_url`, () => {
      App.random_action(`url`)
    }, () => {
      App.random_action(`url`, true)
    }, App.icon(`url`))
  }, show, parent)
}

App.setup_admin_opts = (show = false, parent = ``) => {
  let name = `admin`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.location(`/admin/posts`)
    }, () => {
      App.open_tab(`/admin/posts`)
    }, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.location(`/admin/reactions`)
    }, () => {
      App.open_tab(`/admin/reactions`)
    }, App.icon(`reactions`))

    App.bind_button(`${name}_opts_users`, () => {
      App.location(`/admin/users`)
    }, () => {
      App.open_tab(`/admin/users`)
    }, App.icon(`users`))
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

      App.bind_button(`${name}_opts_${i}`, () => {
        App.open_tab(link.url, link.target)
      }, () => {
        App.open_tab(link.url)
      }, link.icon)
    }
  }, show, parent)
}

App.setup_edit_post_opts = (show = false) => {
  let name = `edit_post`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_title`, () => {
      App.edit_title()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_description`, () => {
      App.edit_description()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_filename`, () => {
      App.edit_filename()
    }, undefined, App.icon(`filename`))

    App.bind_button(`${name}_opts_privacy`, () => {
      App.setup_edit_privacy_opts(true, name)
    }, undefined, App.icon(App.post.privacy))

    App.bind_button(`${name}_opts_delete`, () => {
      let confirm_args = {
        message: `Delete this post`,
        callback_yes: () => {
          App.delete_post()
        },
      }

      App.confirmbox(confirm_args)
    }, undefined, App.icon(`delete`))
  }, show)
}

App.setup_edit_privacy_opts = (show = false, parent = ``) => {
  let name = `edit_privacy`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_public`, () => {
      App.edit_privacy(`public`)
    }, undefined, App.icon(`public`))

    App.bind_button(`${name}_opts_private`, () => {
      App.edit_privacy(`private`)
    }, undefined, App.icon(`private`))
  }, show, parent)
}

App.setup_user_edit_opts = (show = false) => {
  let name = `user_edit`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_poster_no`, () => {
      App.mod_user(`poster`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_reader_no`, () => {
      App.mod_user(`reader`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_reader_yes`, () => {
      App.mod_user(`reader`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_lister_no`, () => {
      App.mod_user(`lister`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_lister_yes`, () => {
      App.mod_user(`lister`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_reacter_no`, () => {
      App.mod_user(`reacter`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_reacter_yes`, () => {
      App.mod_user(`reacter`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_mage_no`, () => {
      App.mod_user(`mage`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_mage_yes`, () => {
      App.mod_user(`mage`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_admin_no`, () => {
      App.mod_user(`admin`, 0, `bool`)
    })

    App.bind_button(`${name}_opts_admin_yes`, () => {
      App.mod_user(`admin`, 1, `bool`)
    })

    App.bind_button(`${name}_opts_rpm`, () => {
      App.user_mod_input(`rpm`, ``, `number`)
    })

    App.bind_button(`${name}_opts_max_size`, () => {
      App.user_mod_input(`max_size`, ``, `number`)
    })

    App.bind_button(`${name}_opts_mark`, () => {
      App.user_mod_input(`mark`, ``, `string`)
    })

    App.bind_button(`${name}_opts_name`, () => {
      App.user_mod_input(`name`, ``, `string`)
    })

    App.bind_button(`${name}_opts_username`, () => {
      App.user_mod_input(`username`, ``, `string`)
    })

    App.bind_button(`${name}_opts_password`, () => {
      App.user_mod_input(`password`, ``, `password`)
    })
  }, show)
}

App.setup_post_edit_opts = (show = false) => {
  let name = `post_edit`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_title`, () => {
      App.edit_post_title()
    }, undefined, App.icon(`edit`))

    App.bind_button(`${name}_opts_public`, () => {
      App.edit_post_privacy(`public`)
    }, undefined, App.icon(`public`))

    App.bind_button(`${name}_opts_private`, () => {
      App.edit_post_privacy(`private`)
    }, undefined, App.icon(`private`))
  }, show)
}

App.setup_page_opts = (show = false) => {
  let name = `page`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_1`, () => {
      App.goto_page(1)
    }, () => {
      App.goto_page(1, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_2`, () => {
      App.goto_page(2)
    }, () => {
      App.goto_page(2, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_3`, () => {
      App.goto_page(3)
    }, () => {
      App.goto_page(3, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_4`, () => {
      App.goto_page(4)
    }, () => {
      App.goto_page(4, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_5`, () => {
      App.goto_page(5)
    }, () => {
      App.goto_page(5, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_6`, () => {
      App.goto_page(6)
    }, () => {
      App.goto_page(6, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_7`, () => {
      App.goto_page(7)
    }, () => {
      App.goto_page(7, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_8`, () => {
      App.goto_page(8)
    }, () => {
      App.goto_page(8, true)
    }, App.icon(`page`))

    App.bind_button(`${name}_opts_9`, () => {
      App.goto_page(9)
    }, () => {
      App.goto_page(9, true)
    }, App.icon(`page`))
  }, show)
}

App.setup_search_opts = (show = false) => {
  let name = `search`

  App.make_opts(name, () => {
    App.bind_button(`${name}_opts_posts`, () => {
      App.prompt_search(`posts`)
    }, undefined, App.icon(`posts`))

    App.bind_button(`${name}_opts_reactions`, () => {
      App.prompt_search(`reactions`)
    }, undefined, App.icon(`reactions`))

    App.bind_button(`${name}_opts_users`, () => {
      App.prompt_search(`users`)
    }, undefined, App.icon(`users`))
  }, show, `menu`)
}