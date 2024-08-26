import { web3Enable, web3Accounts, isWeb3Injected } from 'https://cdn.jsdelivr.net/npm/@polkadot/extension-dapp@latest/+esm';
console.log('talisman is loading')

const ViewUrl = '/fetch/user/';

async function talisman_checking(){
    if (window.injectedWeb3 && window.injectedWeb3.talisman) {

        const extensions = await web3Enable('Talisman Wallet Demo');
        const talismanExtension = extensions.find(ext => ext.name.toLowerCase().includes('talisman'));

        if (!talismanExtension) {
            $.ajax({
                url: "/delete_session/",
                method: "GET",
                success: function(response) {
                    if (response.status === 'success') {
                        alert('please configure talisman or connect your wallet which you used in IAM')
                        window.location.href = '/';
                    } else {
                        alert('please configure talisman or connect your wallet which you used in IAM')
                        window.location.href = '/';
                    }
                },
            });
            
        }
        const allAccounts = await web3Accounts();

        if (allAccounts.length === 0) {
            window.location.href = '/';
        }
        else {
            getUserInfo(allAccounts)
        }
        
    } else {
        console.log("Talisman Wallet not detected. Redirecting to download page.");
        window.open('https://talisman.xyz/download/', '_self');
    }
    
    
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
function getUserInfo(accounts) {
    $.ajax({
        url: ViewUrl,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        data: JSON.stringify({ accounts: accounts}),
        success: function(data) {
            if (data.status === 'success') {
                console.log('User data fetched successfully:', data.user);
                const walletAddress = data.user.wallet_address;

            } else {    
                console.error('Error fetching user data:', data.message);
                alert(data.message)
                window.location.href = '/';

            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error('Request error:', textStatus, errorThrown);
        }
    });
    
}
window.onload =  talisman_checking()