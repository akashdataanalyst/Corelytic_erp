// The form stays read-only and blurred until the editor enters the branding password.
// The server enforces the same rule on save; this only drives the UI.
//
// Once unlocked, the form stays editable for 15 minutes in this login session, and
// every save restarts those 15 minutes. Saving, going to the home page to check the
// result and coming back does not ask for the password again.
//
// The lock state is asked from the server on every refresh: after a save the form
// gets the saved document back without its __onload, so __onload alone would lock
// the form again after each save.

// Browser time (ms) until which the server said the form is unlocked. Lives as long
// as the desk page, so returning to the form from another page needs no request.
let unlocked_until = 0;
let relock_timer = null;

frappe.ui.form.on("Corelytic Branding Settings", {
	onload(frm) {
		const seconds = frm.doc.__onload && frm.doc.__onload.unlocked_seconds;
		if (seconds) remember_unlock(seconds);
	},

	refresh(frm) {
		if (Date.now() < unlocked_until) {
			show_unlocked(frm);
			return;
		}
		// Hide the values until the server answers.
		set_blurred(frm, true);
		frappe.xcall("corelytic_erp.branding.unlock_status").then((seconds) => {
			if (seconds > 0) {
				remember_unlock(seconds);
				show_unlocked(frm);
			} else {
				show_locked(frm);
			}
		});
	},
});

function remember_unlock(seconds) {
	unlocked_until = Date.now() + seconds * 1000;
}

function show_unlocked(frm) {
	set_blurred(frm, false);
	const minutes = Math.max(1, Math.round((unlocked_until - Date.now()) / 60000));
	frm.dashboard.set_headline(
		__("Editing unlocked for {0} more minutes. Each save restarts the 15 minutes.", [minutes]),
		"green"
	);
	// Lock the open form when the time runs out (unless it was saved meanwhile,
	// which the server check then reports).
	clearTimeout(relock_timer);
	relock_timer = setTimeout(() => {
		if (cur_frm && cur_frm.doctype === frm.doctype) {
			unlocked_until = 0;
			cur_frm.refresh();
		}
	}, unlocked_until - Date.now() + 1000);
}

function show_locked(frm) {
	unlocked_until = 0;
	frm.disable_form();
	set_blurred(frm, true);
	frm.dashboard.set_headline(__("These settings are locked. Click Unlock to Edit and enter the password."), "orange");
	frm.page.set_primary_action(__("Unlock to Edit"), () => {
		const dialog = new frappe.ui.Dialog({
			title: __("Unlock Branding Settings"),
			fields: [{ fieldname: "password", fieldtype: "Password", label: __("Password"), reqd: 1 }],
			primary_action_label: __("Unlock"),
			primary_action({ password }) {
				frappe.xcall("corelytic_erp.branding.unlock", { password }).then((seconds) => {
					remember_unlock(seconds);
					dialog.hide();
					// disable_form() marks every field read-only and is not reversible,
					// so start from a fresh page load.
					window.location.reload();
				});
			},
		});
		dialog.show();
	});
}

function set_blurred(frm, blurred) {
	const style = blurred
		? { filter: "blur(6px)", "user-select": "none", "pointer-events": "none" }
		: { filter: "", "user-select": "", "pointer-events": "" };
	$(frm.layout.wrapper).css(style);
	$(frm.page.sidebar).find(".form-attachments").css(style);
}
