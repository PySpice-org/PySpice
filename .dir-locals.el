;; Contains all the default values from:
;; https://github.com/python-lsp/python-lsp-server/blob/develop/pylsp/config/schema.json
;; From looking at the server output, some plugins support additional options.
;; `jsonrpc--json-encode' calls `json-serialize' with (:false-object :json-false) and (:null-object nil).

;; ((nil
;;   . ((eglot-workspace-configuration
;;       . (:pylsp (:plugins (:jedi_completion (:include_params t
;;                                              :fuzzy t)
;;                            :pylint (:enabled t)))
;;          :gopls (:usePlaceholders t)))))
;;  (python-base-mode . ((indent-tabs-mode . nil)))
;;  (go-mode          . ((indent-tabs-mode . t))))

((python-ts-mode
  . ((eglot-workspace-configuration
      . ((pylsp
	  . ((configurationSources . ["pycodestyle"])
	     (plugins
              (autopep8 (enabled . :json-false))
              (pylsp_black (enabled . t))
	      (pyls_isort (enabled . t))
	      (flake8
	       (config . nil)
	       (enabled . :json-false)
	       (exclude . nil)
	       (executable . "flake8")
	       (filename . nil)
	       (hangClosing . nil)
	       (ignore . nil)
	       (maxLineLength . nil)
	       (indentSize . nil)
	       (perFileIgnores . nil)
	       (select . nil))
	      (jedi (extra_paths . [])
		    (env_vars . nil)
		    (environment . nil))
	      (jedi_completion
	       (enabled . t)
	       (include_params . t)
	       (include_class_objects . t)
	       (fuzzy . :json-false)
	       (eager . :json-false)
	       (resolve_at_most . 25)
	       (cache_for . ["pandas" "numpy" "tensorflow" "matplotlib"]))
	      (jedi_definition
	       (enabled . t)
	       (follow_imports . t)
	       (follow_builtin_imports . t))
	      (jedi_hover
	       (enabled . t))
	      (jedi_references
	       (enabled . t))
	      (jedi_signature_help
	       (enabled . t))
	      (jedi_symbols
	       (enabled . t)
	       (all_scopes . t)
	       (include_import_symbols . t))
	      (mccabe
	       (enabled . t)
	       (threshold . 15))
	      (preload
	       (enabled . t)
	       (modules . nil))
	      (pycodestyle
	       (enabled . t)
	       (exclude . nil)
	       (filename . nil)
	       (select . nil)
	       (ignore . nil)
	       (hangClosing . nil)
	       (maxLineLength . nil)
	       (indentSize . nil))
	      (pydocstyle
	       (enabled . :json-false)
	       (convention . nil)
	       (addIgnore . nil)
	       (addSelect . nil)
	       (ignore . nil)
	       (select . nil)
	       (match . "(?!test_).*\\.py")
	       (matchDir . "[^\\.].*"))
	      (pyflakes (enabled . t))
	      (pylint
	       (enabled . t)
	       (args . nil)
	       (executable . nil))
	      (rope_completion
	       (enabled . t)
	       (eager . :json-false))
	      (yapf (enabled . t))))))))))
